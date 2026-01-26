from langchain_core.messages import HumanMessage
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live

console = Console()

def run_cli2(app):
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




def run_cli(app):
    config = {"configurable": {"thread_id": "user_1234"}}
    debug_mode = False # Start with debug OFF

    console.print(Panel.fit(
        "[bold green]💹 Agentic Investment Analyst Online[/bold green]\n"
        "[dim]Type '--debug' to toggle memory inspection.[/dim]",
        border_style="cyan"
    ))

    while True:
        try:
            user_input = input("\n[Query]: ").strip()

            # 1. Handle UI Commands
            if user_input.lower() in ["exit", "quit"]:
                break

            if user_input.lower() == "--debug":
                debug_mode = not debug_mode
                status = "[bold green]ON[/bold green]" if debug_mode else "[bold red]OFF[/bold red]"
                console.print(f"🛠️  Debug Mode is now {status}")
                continue # Skip the rest of the loop and wait for next input

            # 2. Prepare Graph Input
            state_input = {"messages": [HumanMessage(content=user_input)]}

            # 3. Stream Graph Execution
            for event in app.stream(state_input, config=config):
                for node_name, output in event.items():
                    console.print(f"\n[dim]➔ Finished Node:[/dim] [bold magenta]{node_name}[/bold magenta]")

                    # --- CONDITIONAL DEBUG SECTION ---
                    if debug_mode:
                # ... inside the debug section ...
                        current_state = app.get_state(config)
                        messages = current_state.values.get("messages", [])
                        # 1. Update the Column definition to allow wrapping
                        debug_table = Table(title="🪲 Message State Debugger", show_header=True, header_style="bold cyan")
                        debug_table.add_column("Type", style="dim", width=15)
                        debug_table.add_column("Content", overflow="fold") # <--- Magic happens here
                        debug_table.add_column("ID", style="dim", width=10)

                        for msg in messages:
                            msg_type = msg.__class__.__name__
                            color = "green" if "Human" in msg_type else "yellow"
                            if "System" in msg_type: color = "blue"
                            if "Remove" in msg_type: color = "red"

                            # 2. Logic Change: Don't slice the SystemMessage!
                            # We want to see the full summary, but maybe still truncate
                            # massive raw DB results if they are too long.
                            content = msg.content
                            if len(content) > 500: # Only truncate if it's truly massive
                                content = content[:500] + "... [TRUNCATED]"

                            debug_table.add_row(f"[{color}]{msg_type}[/{color}]", content, str(msg.id)[:8])

                        console.print(debug_table)

                    # --- END DEBUG SECTION ---

                    # 4. Standard Output Logic
                    if node_name == "generate_sql" and "sql_query" in output:
                        console.print(f"[dim]Generated SQL:[/dim] [cyan]{output['sql_query']}[/cyan]")

                    if node_name == "analysis" and "analysis" in output:
                        console.print(Panel(output["analysis"], title="[bold green]📊 Analyst Insight[/bold green]", border_style="green"))

        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[bold red]❌ Error:[/bold red] {e}")

    console.print("\n[bold yellow]Session saved. Goodbye![/bold yellow]")