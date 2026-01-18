from langgraph.graph import StateGraph, START, END
from .state import AgentState
from .nodes import generate_sql_node, guardrail_node, execute_query_node, analysis_node, human_review_node

def should_continue(state: AgentState):
    if state["error"] and state["attempts"] < 3:
        return "generate_sql" # Retry loop
    return "analysis"

workflow = StateGraph(AgentState)
workflow.add_node("generate_sql", generate_sql_node)
workflow.add_node("guardrail", guardrail_node)
workflow.add_node("execute_query", execute_query_node)
workflow.add_node("analysis", analysis_node)
workflow.add_node("human_review", human_review_node)

workflow.add_edge(START, "generate_sql")
workflow.add_edge("generate_sql", "guardrail")
workflow.add_edge("guardrail", "human_review")
workflow.add_edge("human_review", "execute_query")
workflow.add_conditional_edges("execute_query", should_continue)
workflow.add_edge("analysis", END)

app = workflow.compile()