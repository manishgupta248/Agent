from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

from config.settings import TELEGRAM_BOT_TOKEN
from core.logger import logger


async def echo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    logger.info(f"Received Telegram message: {user_text}")
    await update.message.reply_text(f"You said: {user_text}")


def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_handler))

    logger.info("Telegram echo bot is running. Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()