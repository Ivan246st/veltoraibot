import os
import csv
import asyncio
from telegram import Update, constants
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes
)

# Змінні середовища
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 5475497037  # твій Telegram ID
CHANNEL_USERNAME = "veltortoken"
CSV_FILE = "users.csv"
MAX_USERS = 1500

# Завантаження вже збережених адрес
submitted_users = set()
if os.path.exists(CSV_FILE):
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        submitted_users = set(row[0] for row in reader)

# Збереження нової адреси
def save_address(user_id, username, eth_address):
    with open(CSV_FILE, "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([user_id, username, eth_address])

# Обробка /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id in submitted_users:
        await update.message.reply_text("Ти вже надсилав адресу. Очікуй на дроп.")
        return
    await update.message.reply_text(
        "✅ Щоб отримати токени, підпишіться на канал https://t.me/veltortoken та запросіть 10 друзів.\n"
        "Після цього надішли свій Ethereum-адрес у цьому чаті."
    )

# Обробка адрес
async def handle_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or "none"
    text = update.message.text.strip()

    if not text.startswith("0x") or len(text) != 42:
        await update.message.reply_text("Невірна Ethereum-адреса. Перевір ще раз.")
        return

    if user_id in submitted_users:
        await update.message.reply_text("Ти вже надсилав адресу. Очікуй на дроп.")
        return

    submitted_users.add(user_id)
    save_address(user_id, username, text)
    await update.message.reply_text("✅ Адресу збережено. Очікуй на дроп після перевірки!")

    # Надсилаємо CSV-файл адміну кожні 50 записів
    if len(submitted_users) % 50 == 0:
        await context.bot.send_document(chat_id=ADMIN_ID, document=open(CSV_FILE, "rb"))

# /export — тільки для адміністратора
async def export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("У тебе немає доступу до цієї команди.")
        return
    await context.bot.send_document(chat_id=ADMIN_ID, document=open(CSV_FILE, "rb"))

# Головна функція
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("export", export))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_address))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
