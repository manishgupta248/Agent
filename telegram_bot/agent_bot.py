import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_ALLOWED_CHAT_ID
from core.logger import logger
from agents.file_agent_graph import build_file_agent_graph


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id

    if chat_id != TELEGRAM_ALLOWED_CHAT_ID:
        logger.warning(f"Blocked unauthorized chat_id: {chat_id}")
        return  # silently ignore — don't reveal the bot is doing anything

    user_text = update.message.text
    logger.info(f"Telegram message from {chat_id}: {user_text}")
    ...

# Build the graph once, reuse across all messages (avoids rebuilding per-request)
agent_app = build_file_agent_graph()

def run_agent_sync(user_text: str) -> str:
    """Blocking call — runs in a background thread, see message_handler below."""
    result = agent_app.invoke(
        {"messages": [{"role": "user", "content": user_text}]},
        config={"recursion_limit": 15},
    )
    return result["messages"][-1]["content"]


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    chat_id = update.message.chat_id
    logger.info(f"Telegram message from {chat_id}: {user_text}")

    # Let the user know the agent is working (tool calls can take a few seconds)
    await update.message.chat.send_action(action="typing")

    try:
        answer = await asyncio.to_thread(run_agent_sync, user_text)
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