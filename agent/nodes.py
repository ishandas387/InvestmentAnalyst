import os

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

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
def generate_sql_node_deprecated(state):
    llm = get_model()
    schema = db_manager.get_schema()

    error_msg = f"\nKeep in mind the previous error: {state['error']}" if state['error'] else ""

    prompt = f"You are a SQLite expert. Given this schema:\n{schema}\n{error_msg}\nWrite a SQL query for: {state['question']}. Return ONLY raw SQL."
    res = llm.invoke([SystemMessage(content=prompt), HumanMessage(content=state['question'])])

    return {"sql_query": res.content.strip(), "attempts": state.get("attempts", 0) + 1}


def generate_sql_node(state):
    llm = get_model() # Using the OpenRouter config we built

    # 1. Define the System Prompt with the Schema
    # We tell the LLM how to handle the history
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a Senior SQL Expert for an investment firm.
        Your goal is to write SQLite queries based on user questions.
        
        DB SCHEMA:
        {schema}
        
        INSTRUCTIONS:
        - Use the conversation history to understand context (e.g., 'it', 'those', 'same again').
        - If the user provides a follow-up, modify the previous logic accordingly.
        - Return ONLY the SQL query. No explanation. No markdown blocks."""),

        # 2. This placeholder injects the entire conversation history automatically
        MessagesPlaceholder(variable_name="messages"),
    ])

    # 3. Get the database schema (from our manager)

    db = DatabaseManager()
    schema = db.get_schema()

    # 4. Chain it together and invoke
    chain = prompt | llm

    # We pass the 'messages' from the state directly
    response = chain.invoke({
        "schema": schema,
        "messages": state["messages"]
    })

    return {"sql_query": response.content}

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

def analysis_node_deprecated(state):
    llm = get_model()
    prompt = f"Analyze these results: {state['db_results']} for the question: {state['question']}"
    res = llm.invoke(prompt)
    return {"analysis": res.content}

def analysis_node(state):
    llm = get_model()

    # 1. Define the Senior Analyst prompt
    # We include the database results as a system context
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a Senior Investment Analyst. 
        Your task is to take the provided database results and explain them to the user.
        
        DATABASE RESULTS:
        {db_results}
        
        INSTRUCTIONS:
        - Use the conversation history to provide a context-aware response.
        - Be professional, concise, and highlight key financial findings.
        - If the results are empty, explain that no data was found for their specific criteria."""),

        # 2. Injects the message history so the AI knows what the user asked
        MessagesPlaceholder(variable_name="messages"),
    ])

    # 3. Create the chain
    chain = prompt | llm

    # 4. Invoke with current state data
    # We pass the history (messages) and the raw SQL results
    response = chain.invoke({
        "messages": state["messages"],
        "db_results": state["db_results"]
    })

    # 5. Update the state
    # We return 'analysis' for your specific field and append the AI's response to 'messages'
    return {
        "analysis": response.content,
        "messages": [response] # The 'add_messages' reducer handles the list append
    }