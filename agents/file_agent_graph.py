import json
from langgraph.graph import StateGraph, END
from groq import BadRequestError

from agents.graph_state import AgentState
from core.llm_router import call_groq_with_tools
from core.logger import logger
from tools.tool_registry import TOOL_FUNCTIONS, TOOL_SCHEMAS

SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are a local file assistant. Use the available tools to "
        "read or write files in the data folder when needed. "
        "Give a clear final answer once you have the information."
    ),
}


def agent_node(state: AgentState) -> dict:
    messages = [SYSTEM_PROMPT] + state["messages"]

    try:
        response = call_groq_with_tools(messages, TOOL_SCHEMAS)
    except BadRequestError as e:
        if "tool_use_failed" in str(e):
            logger.warning(f"Tool call generation failed, retrying once: {e}")
            response = call_groq_with_tools(messages, TOOL_SCHEMAS)
        else:
            raise

    msg = response.choices[0].message

    # Convert Groq SDK message object -> plain dict
    msg_dict = {
        "role": "assistant",
        "content": msg.content,
    }
    if msg.tool_calls:
        msg_dict["tool_calls"] = [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                },
            }
            for tc in msg.tool_calls
        ]

    return {"messages": [msg_dict]}


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

        results.append(
            {
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": str(result),
            }
        )

    return {"messages": results}


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