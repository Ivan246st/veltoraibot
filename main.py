import os
import csv
import asyncio
from telegram import Update, constants
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes
)

# Дані з оточення
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 5475497037  # Твій Telegram ID
CHANNEL_USERNAME = "veltortoken"
CSV_FILE = "users.csv"
MAX_USERS = 1500
EXPORT_EVERY = 50

submitted_users = []

if os.path.exists(CSV_FILE):
    with open(CSV_FILE, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        submitted_users = [row[0] for row in reader]

def save_address(user_id, username, eth_address):
    with open(CSV_FILE, "a", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([user_id, username, eth_address])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)

    if user_id in submitted_users:
        await update.message.reply_text("Ти вже надіслав адресу. Очікуй на дроп.")
        return

    await update.message.reply_text(
        "✅ Щоб отримати токени, підпишіться на канал https://t.me/veltortoken та запросіть 10 друзів.\n\n"
        "Коли все буде виконано — натисни /start ще раз і надішли свою Ethereum-адресу."
    )

async def handle_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)

    if user_id in submitted_users:
        await update.message.reply_text("Ти вже надіслав адресу.")
        return

    text = update.message.text.strip()
    if not text.startswith("0x") or len(text) != 42:
        await update.message.reply_text("Невірна Ethereum-адреса. Перевір і надішли ще раз.")
        return

    save_address(user_id, user.username or "", text)
    submitted_users.append(user_id)

    await update.message.reply_text("Дякую! Адресу збережено — очікуйте на дроп до кінця травня.")

    # Автоекспорт кожні EXPORT_EVERY записів
    if len(submitted_users) % EXPORT_EVERY == 0:
        await context.bot.send_document(
            chat_id=ADMIN_ID,
            document=open(CSV_FILE, "rb"),
            caption="Автоматичний експорт CSV"
        )

async def export_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("У тебе немає доступу до цієї команди.")
        return

    if os.path.exists(CSV_FILE):
        await update.message.reply_document(document=open(CSV_FILE, "rb"))
    else:
        await update.message.reply_text("Файл CSV ще не створено.")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("export", export_csv))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_address))

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
