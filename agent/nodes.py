import os

from db.dbmanager import DatabaseManager
from rich.prompt import Prompt, Confirm
from rich.console import Console


from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

db_manager = DatabaseManager()
# Then initialize it
console = Console()

def get_model():
    # Use the specific OpenRouter base URL
    base_url = "https://openrouter.ai/api/v1"
    # Ensure your .env has OPENROUTER_API_KEY
    api_key = os.getenv("OPENAI_API_KEY")

    return ChatOpenAI(
        model="openai/gpt-oss-20b:free", # The exact string from OpenRouter
        openai_api_key=api_key,
        base_url=base_url,
        # OpenRouter often requires these headers for rankings/analytics
        # default_headers={
        #     "HTTP-Referer": "http://localhost:3000", # Your site URL
        #     "X-Title": "Investment Analyst Agent",   # Your site name
        # }
    )
def generate_sql_node(state):
    llm = get_model()
    schema = db_manager.get_schema()

    error_msg = f"\nKeep in mind the previous error: {state['error']}" if state['error'] else ""

    prompt = f"You are a SQLite expert. Given this schema:\n{schema}\n{error_msg}\nWrite a SQL query for: {state['question']}. Return ONLY raw SQL."
    res = llm.invoke([SystemMessage(content=prompt), HumanMessage(content=state['question'])])

    return {"sql_query": res.content.strip(), "attempts": state.get("attempts", 0) + 1}

def guardrail_node(state):
    query = state["sql_query"].upper()
    if any(word in query for word in ["DROP", "DELETE", "UPDATE", "INSERT"]):
        return {"error": "Security check failed: Read-only access only."}
    return {"error": ""}

def human_review_node(state):
    console.print(f"\n[bold yellow]🔍 AI PROPOSED QUERY:[/bold yellow]")
    console.print(f"[green]{state['sql_query']}[/green]\n")

    choice = Prompt.ask(
        "Do you want to [bold g]Run[/bold g], [bold r]Reject[/bold r], or [bold c]Edit[/bold c]?",
        choices=["g", "r", "c"],
        default="g"
    )

    if choice == "g":
        return {"user_approved": True, "error": ""}
    elif choice == "c":
        new_sql = Prompt.ask("[bold cyan]Enter modified SQL[/bold cyan]")
        return {"sql_query": new_sql, "user_approved": True, "error": ""}
    else:
        return {"user_approved": False, "error": "User rejected the query."}

def execute_query_node(state):
    if state["error"]: return state
    try:
        results = db_manager.execute_query(state["sql_query"])
        return {"db_results": str(results), "error": ""}
    except Exception as e:
        return {"error": str(e)}

def analysis_node(state):
    llm = get_model()
    prompt = f"Analyze these results: {state['db_results']} for the question: {state['question']}"
    res = llm.invoke(prompt)
    return {"analysis": res.content}