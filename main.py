import logging
import csv
import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)

# Змінні середовища
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = 5475497037
CSV_FILE = "wallets.csv"
MAX_WALLETS = 1500

# Логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Flask для Render
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Veltor Airdrop Bot is running."

def run_flask():
    flask_app.run(host="0.0.0.0", port=10000)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if os.path.exists(CSV_FILE) and sum(1 for _ in open(CSV_FILE)) >= MAX_WALLETS:
        await update.message.reply_text("⛔ Набір учасників завершено. Дякуємо за інтерес!")
        return

    await update.message.reply_text(
        "✅ Щоб отримати токени, підпишіться на канал https://t.me/veltortoken та запросіть 10 друзів.\n"
        "Надішліть свою ETH-адресу з MetaMask (вона починається на 0x…)."
    )

# ETH-адреси
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    address = update.message.text.strip()
    user_id = update.message.from_user.id
    username = update.message.from_user.username or ""

    if not address.startswith("0x") or len(address) != 42:
        await update.message.reply_text("❌ Це не схоже на коректну ETH-адресу з MetaMask. Спробуйте ще раз.")
        return

    current_count = sum(1 for _ in open(CSV_FILE)) if os.path.exists(CSV_FILE) else 0
    if current_count >= MAX_WALLETS:
        await update.message.reply_text("⛔ Набір завершено. Досягнуто ліміт у 1500 учасників.")
        return

    with open(CSV_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([user_id, username, address])

    await update.message.reply_text("✅ Адресу збережено! Дякуємо за участь у Veltor Airdrop.")

    if (current_count + 1) % 50 == 0:
        await context.bot.send_document(chat_id=ADMIN_ID, document=open(CSV_FILE, "rb"))

# /export
async def export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != str(ADMIN_ID):
        await update.message.reply_text("⛔ Ця команда доступна лише адміну.")
        return

    if os.path.exists(CSV_FILE):
        await update.message.reply_document(document=open(CSV_FILE, "rb"))
    else:
        await update.message.reply_text("Файл ще не створено.")

# Запуск
def main():
    threading.Thread(target=run_flask).start()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("export", export))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот працює...")
    app.run_polling()

if __name__ == "__main__":
    main()
