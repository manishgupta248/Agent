import json
from core.llm_router import call_groq_with_tools
from core.logger import logger
from tools.tool_registry import TOOL_FUNCTIONS, TOOL_SCHEMAS
from groq import BadRequestError


def run_file_agent(user_request: str, max_turns: int = 5) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "You are a local file assistant. Use the available tools to "
                "read or write files in the data folder when needed. "
                "Give a clear final answer once you have the information."
            ),
        },
        {"role": "user", "content": user_request},
    ]

    for turn in range(max_turns):

        try:
            response = call_groq_with_tools(messages, TOOL_SCHEMAS)
        except BadRequestError as e:
            if "tool_use_failed" in str(e):
                logger.warning(f"Tool call generation failed, retrying once: {e}")
                response = call_groq_with_tools(messages, TOOL_SCHEMAS)
            else:
                raise

        message = response.choices[0].message

        if not message.tool_calls:
            logger.info("Agent produced final answer.")
            return message.content

        # Append the assistant's tool-call message to history
        messages.append(message)

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            logger.info(f"Agent calling tool: {tool_name}({tool_args})")

            if tool_name not in TOOL_FUNCTIONS:
                result = f"Error: unknown tool '{tool_name}'"
            else:
                try:
                    result = TOOL_FUNCTIONS[tool_name](**tool_args)
                except Exception as e:
                    result = f"Error running {tool_name}: {e}"
                    logger.error(result)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result),
                }
            )

    logger.warning("Max turns reached without final answer.")
    return "Agent did not reach a final answer within the turn limit."