import asyncio
import schedule
import time
import telegram

from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_ALLOWED_CHAT_ID
from core.logger import logger
from agents.file_agent_graph import run_agent_with_history
from memory.chat_memory import load_history, save_history, append_user_message, append_assistant_message

BRIEFING_TIME = "07:00"  # 24hr format, local machine time

BRIEFING_PROMPT = (
    "Good morning! Please do the following:\n"
    "1. Check my unread emails and give a concise summary of each — "
    "sender, subject, and one sentence on what action (if any) is needed.\n"
    "2. Check my Google Calendar for events today and the next 2 days.\n"
    "Only report facts from the tool outputs. "
    "End with total unread email count and total upcoming events count."
)


async def _send_telegram_message(text: str):
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    # Telegram messages have a 4096 character limit — split if needed
    if len(text) <= 4096:
        await bot.send_message(chat_id=TELEGRAM_ALLOWED_CHAT_ID, text=text)
    else:
        chunks = [text[i:i+4096] for i in range(0, len(text), 4096)]
        for chunk in chunks:
            await bot.send_message(chat_id=TELEGRAM_ALLOWED_CHAT_ID, text=chunk)


def run_morning_briefing():
    logger.info("Running morning email briefing...")
    try:
        history = load_history(TELEGRAM_ALLOWED_CHAT_ID)
        answer, updated_messages = run_agent_with_history(BRIEFING_PROMPT, history)

        history = append_user_message(history, BRIEFING_PROMPT)
        history = append_assistant_message(history, answer)
        save_history(TELEGRAM_ALLOWED_CHAT_ID, history)

        asyncio.run(_send_telegram_message(f"🌅 *Morning Briefing*\n\n{answer}"))
        logger.info("Morning briefing sent successfully.")

    except Exception as e:
        logger.error(f"Morning briefing failed: {e}")
        asyncio.run(_send_telegram_message("⚠️ Morning briefing failed. Check agent logs."))


def main():
    logger.info(f"Scheduler started. Morning briefing scheduled at {BRIEFING_TIME} daily.")
    schedule.every().day.at(BRIEFING_TIME).do(run_morning_briefing)

    # Run immediately on start so you can test without waiting until 7am
    logger.info("Running initial briefing now for testing...")
    run_morning_briefing()

    while True:
        schedule.run_pending()
        time.sleep(30)  # check every 30 seconds — low CPU cost


if __name__ == "__main__":
    main()