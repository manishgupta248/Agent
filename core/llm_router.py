from groq import Groq
from google import genai
from google.genai import errors as genai_errors

from config.settings import GROQ_API_KEY, GEMINI_API_KEY
from core.logger import logger

groq_client = Groq(api_key=GROQ_API_KEY)
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_MODEL = "openai/gpt-oss-120b"
GEMINI_MODEL = "gemini-2.5-flash"


def _call_groq(messages: list[dict]) -> str:
    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
    )
    return response.choices[0].message.content


def _call_gemini(messages: list[dict]) -> str:
    # Gemini doesn't use the same role/content schema, so flatten to a prompt.
    prompt = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
    response = gemini_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )
    return response.text


def get_llm_response(messages: list[dict]) -> dict:
    """
    Unified entry point for any agent code.
    Tries Groq first, falls back to Gemini on rate-limit/connection errors.
    Returns: {"content": str, "provider": str}  -- provider is for logging only,
    callers are not required to branch on it.
    """
    try:
        logger.info("Attempting Groq (primary)...")
        content = _call_groq(messages)
        logger.info("Groq responded successfully.")
        return {"content": content, "provider": "groq"}

    except Exception as e:
        error_str = str(e).lower()
        is_rate_limit = "429" in error_str or "rate" in error_str
        logger.warning(f"Groq failed ({'rate limit' if is_rate_limit else 'error'}): {e}")
        logger.info("Falling back to Gemini...")

        try:
            content = _call_gemini(messages)
            logger.info("Gemini responded successfully.")
            return {"content": content, "provider": "gemini"}

        except Exception as fallback_error:
            logger.error(f"Gemini fallback also failed: {fallback_error}")
            raise RuntimeError("Both Groq and Gemini failed.") from fallback_error
        

def call_groq_with_tools(messages: list, tools: list):
    """Returns the raw Groq response object (not just text), since we need
    to inspect tool_calls before deciding the next step."""
    return groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=0,
    )