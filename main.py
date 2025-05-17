import logging
import csv
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# Константи
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_USERNAME = "@veltortoken"
CSV_FILE = "eth_addresses.csv"
MAX_USERS = 1500

submitted_users = set()

# Логи
logging.basicConfig(level=logging.INFO)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in submitted_users:
        await update.message.reply_text("✅ Ви вже надіслали адресу. Очікуйте на дроп 20 липня 2025 року.")
        return

    await update.message.reply_text(
        "✅ Щоб отримати токени, підпишіться на канал https://t.me/veltortoken та запросіть 10 друзів.\n"
        "Коли все виконано — натисніть /start ще раз і відправте свою Ethereum-адресу у форматі 0x..."
    )

# Повідомлення з адресою
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    text = update.message.text.strip()

    if len(submitted_users) >= MAX_USERS:
        await update.message.reply_text("❗ Участь у дропі завершено. Стежте за оновленнями в каналі.")
        return

    if not text.startswith("0x") or len(text) != 42:
        await update.message.reply_text("❌ Невірна адреса. Перевірте формат (має починатися з 0x і мати 42 символи).")
        return

    if user_id in submitted_users:
        await update.message.reply_text("❗ Ви вже надіслали адресу.")
        return

    save_address(user_id, user.username or "", text)
    submitted_users.add(user_id)

    await update.message.reply_text("✅ Вашу адресу збережено. Очікуйте на дроп 20 липня 2025 року!")

# Збереження у CSV
def save_address(user_id, username, eth_address):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["user_id", "username", "eth_address"])
        writer.writerow([user_id, username, eth_address])

# Запуск
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == "__main__":
    main()
