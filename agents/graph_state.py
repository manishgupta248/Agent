import operator
from typing import Annotated, TypedDict


class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    tool_call_count: int