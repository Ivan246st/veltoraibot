import csv
import os
import asyncio
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# === КОНСТАНТИ ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "@veltortoken"
MAX_USERS = 1500
CSV_FILE = "users.csv"
ADMIN_ID = 5475497037

submitted_users = {}

# === ФУНКЦІЯ ЗБЕРЕЖЕННЯ АДРЕСИ ===
def save_address(user_id, username, eth_address):
    submitted_users[user_id] = (username, eth_address)
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Username", "Address"])
        for uid, (uname, addr) in submitted_users.items():
            writer.writerow([uid, uname, addr])

# === ФУНКЦІЯ ЗАВАНТАЖЕННЯ ===
def load_submitted_users():
    if not os.path.exists(CSV_FILE):
        return
    with open(CSV_FILE, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            submitted_users[int(row["ID"])] = (row["Username"], row["Address"])

# === СТАРТ ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id in submitted_users:
        await update.message.reply_text("Ви вже надіслали адресу. Очікуйте на дроп 20 липня 2025 року!")
        return
    if len(submitted_users) >= MAX_USERS:
        await update.message.reply_text("Дякуємо за інтерес, але участь у цьому дропі вже завершено.")
        return
    await update.message.reply_text(
        "✅ Щоб отримати токени, підпишіться на канал https://t.me/veltortoken та запросіть 10 друзів."
        "\n\nКоли все буде виконано — натисніть /start ще раз і надішліть свою Ethereum-адресу."
    )

# === ОБРОБКА ETH-АДРЕСИ ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text.strip()
    if user.id in submitted_users:
        return
    if not text.startswith("0x") or len(text) != 42:
        await update.message.reply_text("Невірна Ethereum-адреса. Вона має починатися з 0x та містити 42 символи.")
        return
    if any(addr == text for _, addr in submitted_users.values()):
        await update.message.reply_text("Ця адреса вже була використана.")
        return

    save_address(user.id, user.username or "", text)
    await update.message.reply_text("✅ Вашу адресу збережено. Очікуйте на дроп 20 липня 2025 року!")

    # Якщо кожні 50 — надсилаємо CSV
    if len(submitted_users) % 50 == 0:
        await context.bot.send_document(chat_id=ADMIN_ID, document=InputFile(CSV_FILE))

# === ЕКСПОРТ ТІЛЬКИ ДЛЯ АДМІНА ===
async def export_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if os.path.exists(CSV_FILE):
        await context.bot.send_document(chat_id=ADMIN_ID, document=InputFile(CSV_FILE))

# === ГОЛОВНА ФУНКЦІЯ ===
async def main():
    load_submitted_users()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("export", export_csv))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
