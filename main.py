import os
import csv
import asyncio
import logging
from telegram import Update, InputFile
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# --- Налаштування ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 5475497037  # твій Telegram ID
CHANNEL_USERNAME = "veltortoken"  # назва каналу без @
CSV_FILE = "users.csv"
MAX_USERS = 1500

# --- Ініціалізація логування ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# --- Завантаження існуючих користувачів ---
submitted_users = set()
if os.path.exists(CSV_FILE):
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        submitted_users = {row[0] for row in reader}

# --- Збереження адреси ---
def save_address(user_id, username, eth_address):
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([user_id, username, eth_address])

# --- Обробка /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    if user_id in submitted_users:
        await update.message.reply_text("Ти вже надіслав адресу. Очікуй на дроп.")
        return

    await update.message.reply_text(
        "✅ Щоб отримати токени, підпишіться на канал https://t.me/veltortoken та запросіть 10 друзів.\n\n"
        "Коли все буде виконано — натисни /start ще раз і надішли свою Ethereum-адресу."
    )

# --- Обробка повідомлень (Ethereum адреса) ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or ""
    text = update.message.text.strip()

    if user_id in submitted_users:
        await update.message.reply_text("Ти вже надіслав адресу. Очікуй на дроп.")
        return

    if not text.startswith("0x") or len(text) != 42:
        await update.message.reply_text("Невірна Ethereum-адреса. Спробуй ще раз.")
        return

    save_address(user_id, username, text)
    submitted_users.add(user_id)

    await update.message.reply_text("✅ Адресу збережено. Очікуйте на дроп 28 травня 2025 року!")

    # Якщо кожні 50 нових — надсилаємо файл адміну
    if len(submitted_users) % 50 == 0:
        try:
            with open(CSV_FILE, "rb") as f:
                await context.bot.send_document(chat_id=ADMIN_ID, document=InputFile(f), caption="Нові 50 користувачів.")
        except Exception as e:
            logging.error(f"Не вдалося надіслати CSV файл адміну: {e}")

# --- Обробка /export (тільки для адміна) ---
async def export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("У вас немає доступу до цієї команди.")
        return
    try:
        with open(CSV_FILE, "rb") as f:
            await update.message.reply_document(document=InputFile(f), filename="users.csv")
    except Exception as e:
        await update.message.reply_text(f"Помилка при надсиланні файлу: {e}")

# --- Запуск бота ---
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("export", export))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
