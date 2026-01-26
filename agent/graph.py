import os
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, START, END
from .state import AgentState
from .nodes import generate_sql_node, guardrail_node, execute_query_node, analysis_node, human_review_node, \
    summarize_history_node, visualization_node


def should_continue(state: AgentState):
    if state["error"] and state["attempts"] < 3:
        return "generate_sql" # Retry loop
    return "analysis"
def check_viz_request(state: AgentState):
    if state.get("show_viz"):
        return "visualization"
    return END

conn = sqlite3.connect("agent_memory.db", check_same_thread=False)
memory = SqliteSaver(conn)
workflow = StateGraph(AgentState)
workflow.add_node("summarize", summarize_history_node)
workflow.add_node("generate_sql", generate_sql_node)
workflow.add_node("guardrail", guardrail_node)
workflow.add_node("execute_query", execute_query_node)
workflow.add_node("analysis", analysis_node)
workflow.add_node("human_review", human_review_node)
workflow.add_node("visualization", visualization_node)



workflow.add_edge(START, "summarize")
workflow.add_edge("summarize", "generate_sql")
workflow.add_edge("generate_sql", "guardrail")
workflow.add_edge("guardrail", "human_review")
workflow.add_edge("human_review", "execute_query")
workflow.add_conditional_edges("execute_query", should_continue)
# After analysis, check if we need a chart
workflow.add_conditional_edges(
    "analysis",
    check_viz_request,
    {
        "visualization": "visualization",
        END: END
    }
)
workflow.add_edge("analysis", END)

app = workflow.compile(checkpointer=memory)

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