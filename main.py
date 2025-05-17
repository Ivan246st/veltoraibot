import logging
import csv
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Константи
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "@veltortoken"
MAX_USERS = 1500
CSV_FILE = "wallets.csv"
ADMIN_ID = 5475497037

# Словник для унікальних користувачів
submitted_users = {}

# Налаштування логів
logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in submitted_users:
        await update.message.reply_text("Ви вже надіслали адресу. Очікуйте на дроп.")
        return

    if len(submitted_users) >= MAX_USERS:
        await update.message.reply_text(
            "Дякуємо за інтерес, але участь у цьому дропі вже завершено. "
            "Слідкуйте за новинами у нашому каналі!"
        )
        return

    await update.message.reply_text(
        "✅ Щоб отримати токени, підпишіться на канал https://t.me/veltortoken та запросіть 10 друзів.\n"
        "Коли все виконано — натисніть /start ще раз і надішліть свою Ethereum-адресу."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    text = update.message.text.strip()

    if user_id in submitted_users:
        await update.message.reply_text("Ви вже надіслали адресу.")
        return

    if not text.startswith("0x") or len(text) != 42:
        await update.message.reply_text("Невірна Ethereum-адреса. Має починатися з 0x та містити 42 символи.")
        return

    if text in submitted_users.values():
        await update.message.reply_text("Ця адреса вже використана.")
        return

    submitted_users[user_id] = text

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([user_id, user.username or "", text])

    await update.message.reply_text(
        "Дякуємо! Вашу адресу збережено.\nОчікуйте на дроп 20 липня 2025 року!"
    )

async def export_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("У вас немає прав для цієї команди.")
        return

    if not os.path.exists(CSV_FILE):
        await update.message.reply_text("Файл ще не створено.")
        return

    with open(CSV_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    await update.message.reply_text(f"<code>{content}</code>", parse_mode="HTML")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("export", export_data))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
