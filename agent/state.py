from typing import TypedDict, List

class AgentState(TypedDict):
    question: str
    sql_query: str
    db_results: str
    analysis: str
    error: str
    attempts: int