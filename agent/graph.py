import os

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

def generate_visual_graph():
    graph_filename = "graph_flow.png"
    print(f"📈 Will try to create the graph visual '{graph_filename}'")
    # Only generate if the file does not exist
    if not os.path.exists(graph_filename):
        try:
            # draw_mermaid_png returns the binary data of the image
            png_data = app.get_graph().draw_mermaid_png()
            with open(graph_filename, "wb") as f:
                f.write(png_data)
            print(f"📈 First run detected: Workflow visual saved to '{graph_filename}'")
        except Exception as e:
            print(f"⚠️ Could not generate graph image: {e}")
    else:
        # We skip generation to save resources
        print(f"✅ Workflow visual '{graph_filename}' already exists. Skipping generation.")