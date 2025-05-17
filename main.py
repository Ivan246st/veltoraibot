import logging
import os
import csv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "@veltortoken"
CSV_FILE = "eth_addresses.csv"
MAX_USERS = 1500
submitted_users = set()

logging.basicConfig(level=logging.INFO)

def save_address(user_id, user_name, eth_address):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["user_id", "username", "eth_address"])
        writer.writerow([user_id, user_name, eth_address])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in submitted_users:
        await update.message.reply_text("Ви вже надіслали адресу. Слідкуйте за новинами у нашому каналі!")
        return

    if len(submitted_users) >= MAX_USERS:
        await update.message.reply_text("Дякуємо за інтерес, але участь у цьому дропі вже завершено.")
        return

    await update.message.reply_text(
        "✅ Щоб отримати токени, підпишіться на канал https://t.me/veltortoken та запросіть 10 друзів.\n"
        "Коли все буде виконано — натисніть /start ще раз і надішліть свою Ethereum-адресу."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.username or ""
    text = update.message.text.strip()

    if user_id in submitted_users:
        await update.message.reply_text("Ваша адреса вже збережена.")
        return

    if len(submitted_users) >= MAX_USERS:
        await update.message.reply_text("Дроп завершено — всі 1500 місць заповнено.")
        return

    if text.startswith("0x") and len(text) == 42:
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)
                for row in reader:
                    if text == row[2]:
                        await update.message.reply_text("Ця адреса вже була використана.")
                        return

        save_address(user_id, user_name, text)
        submitted_users.add(user_id)
        await update.message.reply_text("✅ Вашу адресу збережено. Очікуйте на дроп 20 липня 2025 року!")
    else:
        await update.message.reply_text("Невірна адреса. Перевірте формат (має починатися з 0x і мати 42 символи).")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
