"""
MarketSentry CLI Interface.
Runs the multi-agent graph with real-time visual progress rendering.
"""
import sys
import uuid
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from src.graph import build_market_sentry_graph

console = Console()


def print_banner():
    console.print(
        Panel.fit(
            "[bold cyan]MarketSentry[/bold cyan] [white]🛡️ Autonomous Adversarial Market Intelligence Graph[/white]\n"
            "[dim]Zero-Cost • 100% Local Inference • SEC EDGAR + yfinance Grounded[/dim]",
            box=box.DOUBLE,
            border_style="cyan"
        )
    )


def display_thesis(stance: str, thesis):
    if not thesis:
        return
    
    color = "green" if stance == "BULL" else "red"
    table = Table(title=f"{stance} Thesis Evidence Matrix", box=box.ROUNDED, border_style=color)
    table.add_column("Claim / Point", style="bold white", width=35)
    table.add_column("Empirical Metric / Citation", style=color, width=30)
    table.add_column("Confidence", justify="right", style="cyan", width=12)

    for item in thesis.key_points:
        conf = f"{item.confidence_score * 100:.0f}%"
        table.add_row(item.point, item.metric_or_citation, conf)

    console.print(f"\n[bold {color}]{stance} Summary:[/bold {color}] {thesis.summary}")
    console.print(table)


def display_memo(memo):
    if not memo:
        return
    
    verdict_colors = {
        "OVERWEIGHT": "bold green",
        "NEUTRAL": "bold yellow",
        "UNDERWEIGHT": "bold red"
    }
    verdict_style = verdict_colors.get(memo.verdict, "bold white")
    
    table = Table(box=box.HEAVY_EDGE, border_style="cyan", show_header=False)
    table.add_column("Field", style="bold white", width=22)
    table.add_column("Value", style="dim white")

    table.add_row("Ticker Target", memo.ticker)
    table.add_row("Institutional Verdict", f"[{verdict_style}]{memo.verdict}[/{verdict_style}]")
    table.add_row("Conviction Score", f"{memo.conviction_score * 100:.1f}%")
    table.add_row("Primary Growth Catalyst", f"[green]{memo.primary_catalyst}[/green]")
    table.add_row("Primary Risk Vector", f"[red]{memo.primary_risk}[/red]")

    console.print("\n")
    console.print(Panel(table, title="[bold cyan]🏛️ CIO Final Investment Memo[/bold cyan]", border_style="cyan"))
    console.print(Panel(memo.synthesis_memo, title="[dim]Detailed Synthesis & Allocation Rationale[/dim]", box=box.ROUNDED))


def main():
    print_banner()

    ticker = input("\nEnter US Equity Ticker (e.g., NVDA, AAPL, MSFT, TSLA): ").strip().upper()
    if not ticker:
        console.print("[red]Error: Ticker cannot be empty.[/red]")
        sys.exit(1)

    # Initialize graph
    with console.status("[bold green]Compiling MarketSentry LangGraph engine & SQLite checkpointer...", spinner="dots"):
        app = build_market_sentry_graph()

    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    initial_state = {"ticker": ticker}

    console.print(f"\n[cyan]▶ Initializing execution graph for [bold]{ticker}[/bold] (Thread ID: {thread_id[:8]})...[/cyan]")

    # Stream execution node by node
    for step_output in app.stream(initial_state, config=config):
        for node_name, node_state in step_output.items():
            if node_name == "ingestion":
                console.print(f"[green]✓ Ingestion Complete:[/green] Raw market snapshot & SEC 10-K data parsed.")
            
            elif node_name == "bull_analyst":
                console.print(f"[green]✓ Bull Analyst Node Complete:[/green] Upside thesis drafted.")
                display_thesis("BULL", node_state.get("bull_thesis"))
            
            elif node_name == "bear_analyst":
                console.print(f"[red]✓ Bear Analyst Node Complete:[/red] Downside risks formulated.")
                display_thesis("BEAR", node_state.get("bear_thesis"))

            elif node_name == "audit_thesis":
                audit_history = node_state.get("audit_history", [])
                latest_audit = audit_history[-1] if audit_history else None
                round_num = node_state.get("audit_round", 1)
                
                if latest_audit and latest_audit.passes_audit:
                    console.print(f"[cyan]✓ Skeptic Audit [Round {round_num}]: PASSED.[/cyan] Claims verified against 10-K & market metrics.")
                else:
                    console.print(f"[yellow]⚠ Skeptic Audit [Round {round_num}]: CHALLENGED.[/yellow] Triggering reflection revision cycle.")

            elif node_name == "synthesize_memo":
                console.print(f"[bold cyan]✓ Synthesis Node Complete:[/bold cyan] Final trade allocation produced.")
                display_memo(node_state.get("final_memo"))


if __name__ == "__main__":
    main()