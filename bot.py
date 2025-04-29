# bot.py

import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")
TWITTER_HANDLE = os.getenv("TWITTER_HANDLE")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store verified users
verified_users = set()

# --- Task Menu Keyboard ---
def task_menu():
    keyboard = [
        [InlineKeyboardButton("✅ Join Telegram Channel", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")],
        [InlineKeyboardButton("🐦 Follow Twitter", url=f"https://twitter.com/{TWITTER_HANDLE}")],
        [InlineKeyboardButton("📱 Join Whatsapp Group", url="https://chat.whatsapp.com/KyBPEZKLjAZ8JMgFt9KMft")],
        [InlineKeyboardButton("📢 Join Whatsapp Channel", url="https://whatsapp.com/channel/0029VbAXEgUFy72Ich07Z53o")],
        [InlineKeyboardButton("🔍 Verify Tasks", callback_data="verify_tasks")]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- Start Command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎯 To participate in the game, complete the following tasks:\n\n"
        f"1. Join our Telegram channel\n"
        f"2. Follow our Twitter account ({TWITTER_HANDLE})\n"
        f"3. Join our WhatsApp group\n"
        f"4. Join our WhatsApp channel\n\n"
        "After that, click the button below to verify!",
        reply_markup=task_menu()
    )

# --- Verify Tasks ---
async def verify_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    try:
        chat_member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if chat_member.status not in ["member", "administrator", "creator"]:
            raise Exception("Not a member")
    except Exception:
        await query.edit_message_text(
            "❌ You have not joined the Telegram channel. Please complete all tasks first.",
            reply_markup=task_menu()
        )
        return

    # Simulated Twitter check
    keyboard = [[InlineKeyboardButton("✅ I've Followed on Twitter", callback_data="confirm_twitter")]]
    await query.edit_message_text(
        "👀 We can't verify Twitter follows automatically due to API limits.\n\n"
        "Please click the button below *after* you've followed us on Twitter.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# --- Confirm Twitter ---
async def confirm_twitter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    verified_users.add(user_id)

    await query.edit_message_text(
        "✅ Details submitted successfully. You can now use /play to start the game!"
    )

# --- Play Command ---
async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in verified_users:
        await update.message.reply_text(
            "❌ You must complete the tasks first. Use /start to begin."
        )
        return
    await update.message.reply_text("🎮 Welcome to the game! [Insert game logic here...]")

# --- Run Bot ---
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", play))
    app.add_handler(CallbackQueryHandler(verify_tasks, pattern="^verify_tasks$"))
    app.add_handler(CallbackQueryHandler(confirm_twitter, pattern="^confirm_twitter$"))

    app.run_polling()

if __name__ == "__main__":
    main()
