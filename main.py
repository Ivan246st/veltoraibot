import os
import csv
from telegram import Update, constants
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 5475497037  # Твій Telegram ID
CHANNEL_USERNAME = "veltortoken"
CSV_FILE = "users.csv"
MAX_USERS = 1500

submitted_users = set()
if os.path.exists(CSV_FILE):
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        submitted_users = {row[0] for row in reader}

def save_address(user_id, username, eth_address):
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([user_id, username, eth_address])
    submitted_users.add(user_id)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id in submitted_users:
        await update.message.reply_text("Ти вже надіслав адресу. Очікуй на дроп.")
        return

    await update.message.reply_text(
        "✅ Щоб отримати токени, підпишіться на канал https://t.me/veltortoken та запросіть 10 друзів.\n\n"
        "Коли все буде виконано — натисни /start ще раз і надішли свою Ethereum-адресу."
    )

async def handle_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text.strip()

    if user.id in submitted_users:
        await update.message.reply_text("Ти вже відправив адресу. Очікуй на дроп.")
        return

    if not text.startswith("0x") or len(text) != 42:
        await update.message.reply_text("❗ Невірна Ethereum-адреса. Вона має починатися з 0x та містити 42 символи.")
        return

    save_address(str(user.id), user.username or "", text)
    await update.message.reply_text("✅ Адресу збережено. Очікуй на дроп 20 травня 2025 року.")

    if len(submitted_users) % 50 == 0:
        await context.bot.send_document(
            chat_id=ADMIN_ID,
            document=open(CSV_FILE, "rb"),
            filename="users.csv",
            caption="Оновлений список адрес."
        )

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_address))

    app.run_polling(allowed_updates=constants.Update.ALL_TYPES)

if __name__ == "__main__":
    main()
