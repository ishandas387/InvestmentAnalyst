from rich.console import Console
from rich.panel import Panel

console = Console()

def run_cli(app):
    console.print(Panel("[bold green]Agentic Analyst Online[/bold green]"))
    while True:
        q = console.input("\n[bold cyan]Query:[/bold cyan] ")
        if q.lower() in ["exit", "quit"]: break

        state = {"question": q, "error": "", "attempts": 0}
        for event in app.stream(state):
            for node, data in event.items():
                console.print(f"[dim]Finished Node: {node}[/dim]")
                if "analysis" in data:
                    console.print(Panel(data["analysis"], title="Final Result"))