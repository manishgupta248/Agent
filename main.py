import threading
import time
import schedule

from core.logger import logger
from scheduler.morning_briefing import run_morning_briefing, BRIEFING_TIME


def run_scheduler():
    logger.info(f"Scheduler thread started. Briefing at {BRIEFING_TIME} daily.")
    schedule.every().day.at(BRIEFING_TIME).do(run_morning_briefing)
    while True:
        schedule.run_pending()
        time.sleep(30)


def run_telegram_bot():
    # Import here so Telegram's event loop starts inside this thread
    from telegram_bot.agent_bot import main as bot_main
    logger.info("Telegram bot thread started.")
    bot_main()


if __name__ == "__main__":
    logger.info("=== Agent System Starting ===")

    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    # Telegram bot runs in the main thread (it owns the event loop)
    run_telegram_bot()