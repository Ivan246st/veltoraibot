import csv
import os
import asyncio
from telegram import Update, constants
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
)

# === Змінні середовища ===
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 5475497037  # твій Telegram ID
CHANNEL_USERNAME = "veltortoken"
CSV_FILE = "users.csv"
MAX_USERS = 1500

# === Завантаження CSV ===
submitted_users = []
if os.path.exists(CSV_FILE):
    with open(CSV_FILE, newline="", encoding='utf-8') as f:
        reader = csv.reader(f)
        submitted_users = [row[0] for row in reader]

# === Збереження адреси ===
def save_address(user_id, username, eth_address):
    with open(CSV_FILE, "a", newline="", encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([user_id, username, eth_address])

# === Обробка /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)

    if user_id in submitted_users:
        await update.message.reply_text("✅ Ви вже надіслали адресу. Очікуйте на дроп.")
        return

    if len(submitted_users) >= MAX_USERS:
        await update.message.reply_text("❌ Airdrop завершено. Ліміт учасників досягнуто.")
        return

    await update.message.reply_text(
        "✅ Щоб отримати токени, підпишіться на канал https://t.me/veltortoken та запросіть 10 друзів.\n"
        "Коли все буде виконано — натисніть /start ще раз і надішліть свою Ethereum-адресу."
    )

# === Обробка адреси ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    username = f"@{user.username}" if user.username else user.first_name
    text = update.message.text.strip()

    if user_id in submitted_users:
        return await update.message.reply_text("Ваша адреса вже надіслана.")

    if not text.startswith("0x") or len(text) != 42:
        return await update.message.reply_text("❌ Невірний формат адреси. Спробуйте ще раз.")

    save_address(user_id, username, text)
    submitted_users.append(user_id)

    await update.message.reply_text("✅ Адресу збережено. Очікуйте на дроп 28 травня 2025 року.")

    # Кожні 50 — надсилаємо файл адміну
    if len(submitted_users) % 50 == 0:
        if os.path.exists(CSV_FILE):
            await context.bot.send_document(chat_id=ADMIN_ID, document=open(CSV_FILE, "rb"))

# === Обробка /export (тільки для ADMIN_ID) ===
async def export_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID and os.path.exists(CSV_FILE):
        await context.bot.send_document(chat_id=ADMIN_ID, document=open(CSV_FILE, "rb"))
    else:
        await update.message.reply_text("⛔ Ви не маєте прав для цієї команди.")

# === Основна функція ===
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("export", export_csv))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.run_polling()

# === Запуск (сумісно з Render) ===
if __name__ == '__main__':
    import asyncio

    try:
        asyncio.run(main())
    except RuntimeError as e:
        import sys
        if "cannot be called from a running event loop" in str(e) or "There is no current event loop" in str(e):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(main())
        else:
            raise
