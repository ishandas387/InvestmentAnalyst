from langchain_core.messages import HumanMessage
from rich.console import Console
from rich.panel import Panel
from rich.live import Live

console = Console()

def run_cli(app):
    # A hardcoded thread_id ensures memory persists across restarts
    config = {"configurable": {"thread_id": "user_1234"}}

    console.print(Panel.fit(
        "[bold green]💹 Agentic Investment Analyst Online[/bold green]\n"
        "[dim]Memory-backed session (SQLite) is active.[/dim]",
        border_style="cyan"
    ))

    while True:
        try:
            user_input = input("\n[Query]: ")
            if user_input.lower() in ["exit", "quit"]:
                break

            # 1. Wrap input in a HumanMessage for the state's message list
            state_input = {"messages": [HumanMessage(content=user_input)]}

            # 2. Stream the graph execution
            # LangGraph yields updates as each node completes
            for event in app.stream(state_input, config=config):
                for node_name, output in event.items():
                    console.print(f"[dim]➔ Finished Node:[/dim] [bold magenta]{node_name}[/bold magenta]")

                    # 3. Check if the current node is the 'analysis' node
                    # We extract the 'analysis' string from the node's returned dictionary
                    if node_name == "analysis" and "analysis" in output:
                        console.print("\n")
                        console.print(Panel(
                            output["analysis"],
                            title="[bold green]📊 Analyst Insight[/bold green]",
                            title_align="left",
                            border_style="green",
                            padding=(1, 2)
                        ))

                    # 4. (Optional) Show SQL query for transparency
                    if node_name == "generate_sql" and "sql_query" in output:
                        console.print(f"[dim]Generated SQL:[/dim] [cyan]{output['sql_query']}[/cyan]")

        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[bold red]❌ Error:[/bold red] {e}")

    console.print("\n[bold yellow]Session saved. Goodbye![/bold yellow]")