import logging
import asyncio
import platform
import csv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

BOT_TOKEN = "YOUR_BOT_TOKEN"
CHANNEL_USERNAME = "@veltortoken"
MAX_USERS = 1500
CSV_FILE = "addresses.csv"

submitted_users = set()

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def save_address(user_id: int, username: str, address: str):
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([user_id, username, address])
        submitted_users.add(user_id)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if len(submitted_users) >= MAX_USERS:
        await update.message.reply_text("Airdrop завершено. Всі токени були розподілені.")
        return
    if user.id in submitted_users:
        await update.message.reply_text("Ви вже надіслали адресу. Очікуйте на дроп.")
        return
    await update.message.reply_text(
        "✅ Щоб отримати токени, підпишіться на канал https://t.me/veltortoken та запросіть 10 друзів."
        "Коли все буде виконано — натисніть /start ще раз і надішліть свою Ethereum-адресу."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text.strip()
    if user.id in submitted_users:
        return
    if not text.startswith("0x") or len(text) != 42:
        await update.message.reply_text("Невірна Ethereum-адреса. Вона має починатись з 0x та містити 42 символи.")
        return
    save_address(user.id, user.username or "", text)
    await update.message.reply_text("Дякуємо! Вашу адресу збережено. Очікуйте на дроп 20 липня 2025 року!")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
