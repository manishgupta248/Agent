import json
from langgraph.graph import StateGraph, END
from groq import BadRequestError

from agents.graph_state import AgentState
from core.llm_router import call_groq_with_tools
from core.logger import logger
from tools.tool_registry import TOOL_FUNCTIONS, TOOL_SCHEMAS
from core.llm_router import call_groq_with_tools, call_gemini_with_tools

SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are a local file and communication assistant. "
        "Rules:\n"
        "1. Only call a tool if it is necessary to answer the request.\n"
        "2. NEVER invent a filename. Only call read_text_file on a filename "
        "that was explicitly mentioned by the user or that you yourself just "
        "created with write_text_file in this same conversation.\n"
        "3. If a tool result (e.g. fetch_unread_emails) already contains the "
        "information needed to answer, use that information directly — do not "
        "call another tool to 're-read' or 'verify' it.\n"
        "4. Only state facts that are present in the tool outputs or the user's "
        "message. If something is not known, say so explicitly instead of guessing.\n"
        "5. Once you have enough information, stop calling tools and give a "
        "final answer."
    ),
}

MAX_TOOL_CALLS = 6

def agent_node(state: AgentState) -> dict:
    messages = [SYSTEM_PROMPT] + state["messages"]
    tool_call_count = state.get("tool_call_count", 0)

    # Force a final answer instead of crashing once we're near the limit
    if tool_call_count >= MAX_TOOL_CALLS:
        messages.append({
            "role": "system",
            "content": "You have used the maximum number of tool calls. "
                       "Give your best final answer now using only what you already know.",
        })
        try:
            response = call_groq_with_tools(messages, [])  # no tools offered
            msg = response.choices[0].message
            return {"messages": [{"role": "assistant", "content": msg.content}]}
        except Exception:
            return {"messages": [{"role": "assistant", "content": "I wasn't able to complete this request."}]}

    try:
        logger.info("Attempting Groq (primary)...")
        response = call_groq_with_tools(messages, TOOL_SCHEMAS)
        msg = response.choices[0].message

        msg_dict = {"role": "assistant", "content": msg.content}
        if msg.tool_calls:
            msg_dict["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in msg.tool_calls
            ]
        logger.info("Groq responded successfully.")
        return {"messages": [msg_dict]}

    except Exception as e:
        error_str = str(e).lower()
        is_rate_limit = "429" in error_str or "rate" in error_str or "tool_use_failed" in error_str
        logger.warning(f"Groq failed ({'rate limit/tool error' if is_rate_limit else 'error'}): {e}")
        logger.info("Falling back to Gemini for tool-calling...")

        try:
            msg_dict = call_gemini_with_tools(messages, TOOL_SCHEMAS)
            logger.info("Gemini responded successfully.")
            return {"messages": [msg_dict]}
        except Exception as fallback_error:
            logger.error(f"Gemini fallback also failed: {fallback_error}")
            return {"messages": [{"role": "assistant", "content": "I'm having trouble reaching the AI services right now."}]}


def tools_node(state: AgentState) -> dict:
    last_message = state["messages"][-1]
    results = []

    for tool_call in last_message["tool_calls"]:
        tool_name = tool_call["function"]["name"]
        tool_args = json.loads(tool_call["function"]["arguments"])

        logger.info(f"Agent calling tool: {tool_name}({tool_args})")

        if tool_name not in TOOL_FUNCTIONS:
            result = f"Error: unknown tool '{tool_name}'"
        else:
            try:
                result = TOOL_FUNCTIONS[tool_name](**tool_args)
            except Exception as e:
                result = f"Error running {tool_name}: {e}"
                logger.error(result)

        results.append({
            "role": "tool",
            "tool_call_id": tool_call["id"],
            "content": str(result),
        })

    return {
        "messages": results,
        "tool_call_count": state.get("tool_call_count", 0) + 1,
    }


def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if last_message.get("tool_calls"):
        return "tools"
    return END


def build_file_agent_graph():
    graph = StateGraph(AgentState)

    graph.add_node("agent", agent_node)
    graph.add_node("tools", tools_node)

    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")

    return graph.compile()

def run_agent_with_history(user_text: str, history: list) -> tuple[str, list]:
    """
    Runs the agent with pre-loaded conversation history.
    Returns (final_answer, updated_full_message_list).
    """
    app = build_file_agent_graph()

    # Strip timestamps before sending to LLM (it only needs role + content)
    clean_history = [
        {"role": m["role"], "content": m["content"]}
        for m in history
        if m.get("role") in ("user", "assistant") and m.get("content")
    ]

    initial_messages = clean_history + [{"role": "user", "content": user_text}]

    result = app.invoke(
        {"messages": initial_messages, "tool_call_count": 0},
        config={"recursion_limit": 15},
    )

    final_answer = result["messages"][-1]["content"]
    return final_answer, result["messages"]