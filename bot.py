import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ================= CONFIG =================
BOT_TOKEN = "8205388771:AAGKHiEMk3KTD-uJfF-gezfdvWK7sQ5ZfNE"  # Telegram BotFather se lo
ADMIN_ID = 1900664668  # Apna Telegram ID yahan daalna
UPI_ID = "chodhary.pankaj2@ybl"  # Apna UPI ID
UPI_QR_URL = "https://drive.google.com/file/d/1-vFGul2Bo7UOq-J6pzSc9p0C42IOIohc/view?usp=drivesdk"  # UPI QR image ka link

# Plans
PLANS = {
    "3m": {"name": "3 Months", "price": 49},
    "6m": {"name": "6 Months", "price": 79},
    "1y": {"name": "1 Year", "price": 99},
}

# Pending users memory store
pending_payments = {}

# ================= HANDLERS =================

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("3 Months - ₹49", callback_data="plan_3m"),
            InlineKeyboardButton("6 Months - ₹79", callback_data="plan_6m"),
        ],
        [InlineKeyboardButton("1 Year - ₹99", callback_data="plan_1y")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 Welcome!\nChoose your subscription plan:",
        reply_markup=reply_markup,
    )

# Plan selection
async def plan_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    plan_key = query.data.replace("plan_", "")
    plan = PLANS[plan_key]

    pending_payments[query.from_user.id] = plan_key

    await query.message.reply_text(
        f"💳 *Payment Details*\n\n"
        f"Plan: {plan['name']}\nPrice: ₹{plan['price']}\n\n"
        f"UPI ID: `{UPI_ID}`\n"
        f"[Scan QR to Pay]({UPI_QR_URL})\n\n"
        f"⏳ You have 5 minutes to complete the payment.",
        parse_mode="Markdown",
    )

    # Start 5-minute auto-cancel timer
    asyncio.create_task(auto_cancel(query.from_user.id, context))

# Auto cancel payment after 5 mins
async def auto_cancel(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    await asyncio.sleep(300)  # 5 minutes
    if user_id in pending_payments:
        await context.bot.send_message(
            chat_id=user_id,
            text="⛔ Payment time expired! Please try again.",
        )
        del pending_payments[user_id]

# Approve payment (admin only)
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ You are not authorized to approve payments!")
        return

    try:
        user_id = int(context.args[0])
        link = context.args[1]
    except:
        await update.message.reply_text("❌ Usage: /approve <user_id> <link>")
        return

    if user_id in pending_payments:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"✅ Payment Successful!\nYour download link: {link}",
        )
        del pending_payments[user_id]
        await update.message.reply_text(f"✅ Link sent to user {user_id}!")
    else:
        await update.message.reply_text("❌ No pending payment found for this user.")

# Buy command for retry
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

# ================= MAIN =================
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("buy", buy))
app.add_handler(CommandHandler("approve", approve))
app.add_handler(CallbackQueryHandler(plan_selected))

print("✅ Bot is running...")
app.run_polling()
