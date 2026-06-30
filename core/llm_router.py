import json
from groq import Groq
from google import genai
from google.genai import errors as genai_errors
from google.genai import types as genai_types

from config.settings import GROQ_API_KEY, GEMINI_API_KEY
from core.logger import logger

groq_client = Groq(api_key=GROQ_API_KEY)
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_MODEL = "openai/gpt-oss-120b"
# GROQ_MODEL = "xyz"
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


def _convert_tools_to_gemini(tools: list) -> list:
    function_declarations = []
    for tool in tools:
        fn = tool["function"]
        function_declarations.append(
            genai_types.FunctionDeclaration(
                name=fn["name"],
                description=fn["description"],
                parameters=fn["parameters"],
            )
        )
    return [genai_types.Tool(function_declarations=function_declarations)]


def call_gemini_with_tools(messages: list, tools: list):
    """Returns a normalized dict (not the raw Gemini response), since Gemini's
    response shape differs significantly from Groq's."""
    # Flatten chat history into Gemini's expected format
    contents = []
    for m in messages:
        if m["role"] == "system":
            continue  # handled separately below
        role = "model" if m["role"] == "assistant" else "user"
        if m["role"] == "tool":
            contents.append(
                genai_types.Content(
                    role="user",
                    parts=[genai_types.Part(text=f"Tool result: {m['content']}")],
                )
            )
        else:
            contents.append(
                genai_types.Content(role=role, parts=[genai_types.Part(text=m["content"] or "")])
            )

    system_msgs = [m["content"] for m in messages if m["role"] == "system"]
    system_instruction = system_msgs[0] if system_msgs else None

    gemini_tools = _convert_tools_to_gemini(tools)

    response = gemini_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config=genai_types.GenerateContentConfig(
            tools=gemini_tools,
            system_instruction=system_instruction,
        ),
    )

    candidate = response.candidates[0]
    tool_calls = []
    text_content = None

    for part in candidate.content.parts:
        if part.function_call:
            tool_calls.append(
                {
                    "id": f"gemini_call_{len(tool_calls)}",
                    "type": "function",
                    "function": {
                        "name": part.function_call.name,
                        "arguments": json.dumps(dict(part.function_call.args)),
                    },
                }
            )
        elif part.text:
            text_content = part.text

    return {
        "role": "assistant",
        "content": text_content,
        "tool_calls": tool_calls if tool_calls else None,
    }