import logging
import csv
import os
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, ContextTypes, filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "@veltortoken"
CSV_FILE = "eth_addresses.csv"
MAX_USERS = 1500
submitted_users = set()

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if user.id in submitted_users:
        await update.message.reply_text("Ви вже надіслали адресу. Слідкуйте за новинами у каналі.")
        return

    await update.message.reply_text(
        "✅ Щоб отримати токени, підпишіться на канал https://t.me/veltortoken та запросіть 10 друзів.\n"
        "Коли все буде виконано — натисніть /start ще раз і надішліть свою Ethereum-адресу."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text.strip()

    if user.id in submitted_users:
        return

    if len(submitted_users) >= MAX_USERS:
        await update.message.reply_text("Дякуємо за інтерес, але участь у цьому дропі вже завершено. Слідкуйте за новинами у каналі.")
        return

    if text.startswith("0x") and len(text) == 42:
        if not os.path.exists(CSV_FILE):
            with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["user_id", "username", "eth_address"])

        with open(CSV_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if text == row[-1]:
                    await update.message.reply_text("Ця Ethereum-адреса вже була зареєстрована.")
                    return

        with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([user.id, user.username or "", text])
            submitted_users.add(user.id)

        await update.message.reply_text("✅ Дякуємо! Вашу адресу збережено. Очікуйте на дроп 20 липня 2025 року!")
    else:
        await update.message.reply_text("❌ Невірна адреса. Перевірте формат (має починатися з 0x і мати 42 символи).")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
