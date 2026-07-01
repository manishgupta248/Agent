import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_ALLOWED_CHAT_ID
from core.logger import logger
from agents.file_agent_graph import build_file_agent_graph, run_agent_with_history
from memory.chat_memory import (
    load_history,
    save_history,
    append_user_message,
    append_assistant_message,
)

agent_app = build_file_agent_graph()


def run_agent_sync(user_text: str, chat_id: int) -> str:
    history = load_history(chat_id)
    logger.info(f"Loaded {len(history)} messages from memory for chat {chat_id}")

    answer, updated_messages = run_agent_with_history(user_text, history)

    history = append_user_message(history, user_text)
    history = append_assistant_message(history, answer)
    save_history(chat_id, history)
    logger.info(f"Saved updated memory for chat {chat_id}")

    return answer


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id

    if chat_id != TELEGRAM_ALLOWED_CHAT_ID:
        logger.warning(f"Blocked unauthorized chat_id: {chat_id}")
        return

    user_text = update.message.text
    logger.info(f"Telegram message from {chat_id}: {user_text}")

    await update.message.chat.send_action(action="typing")

    try:
        answer = await asyncio.to_thread(run_agent_sync, user_text, chat_id)
    except Exception as e:
        logger.error(f"Agent error: {e}")
        answer = "Sorry, something went wrong while processing your request."

    await update.message.reply_text(answer)


def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    logger.info("Telegram AGENT bot is running. Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()