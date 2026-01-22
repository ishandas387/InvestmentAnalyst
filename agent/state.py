from typing import TypedDict, List, Annotated

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


class AgentState(TypedDict):
    # 'add_messages' ensures new messages are appended to the list, not overwritten
    messages: Annotated[List[BaseMessage], add_messages]

    sql_query: str
    db_results: str
    analysis: str
    error: str
    attempts: int