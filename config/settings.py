import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_ALLOWED_CHAT_ID = int(os.getenv("TELEGRAM_ALLOWED_CHAT_ID", "0"))

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Check your .env file.")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found. Check your .env file.")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found. Check your .env file.")

if not TELEGRAM_ALLOWED_CHAT_ID:
    raise ValueError("TELEGRAM_ALLOWED_CHAT_ID not found. Check your .env file.")