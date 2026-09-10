"""
MarketSentry Autonomous Sentinel Daemon.
Continuously scans a watchlist, identifies quantitative market anomalies,
and triggers the dialectic multi-agent audit graph without human intervention.
"""
import time
import uuid
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from src.tools.anomaly_detector import MarketSentinel
from src.graph import build_market_sentry_graph

console = Console()

WATCHLIST = ["NVDA", "TSLA", "AAPL", "MSFT", "GOOGL", "AMZN", "AMD"]


def render_sentinel_banner():
    console.print(
        Panel.fit(
            "[bold red]MarketSentry Sentinel Engine[/bold red] [white]📡 Real-Time Autonomous Market Monitor[/white]\n"
            "[dim]Continuous Watchlist Ingestion • Statistical Anomaly Detection • Autonomous Graph Dispatch[/dim]",
            box=box.DOUBLE,
            border_style="red"
        )
    )


def run_autonomous_audit(ticker: str, trigger_info: dict):
    console.print(f"\n[bold yellow]⚡ ANOMALY DETECTED FOR {ticker}![/bold yellow]")
    for t in trigger_info.get("triggers", []):
        console.print(f"  [red]▶ {t}[/red]")

    console.print(f"\n[cyan]🤖 Dispatching MarketSentry Multi-Agent Graph for forensic analysis on {ticker}...[/cyan]")
    
    app = build_market_sentry_graph()
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    initial_state = {"ticker": ticker}

    final_memo = None

    for step_output in app.stream(initial_state, config=config):
        for node_name, node_state in step_output.items():
            if node_name == "bull_analyst":
                console.print(f"  [green]✓ Bull Analyst completed thesis.[/green]")
            elif node_name == "bear_analyst":
                console.print(f"  [red]✓ Bear Analyst completed risk analysis.[/red]")
            elif node_name == "audit_thesis":
                audits = node_state.get("audit_history", [])
                latest = audits[-1] if audits else None
                round_num = node_state.get("audit_round", 1)
                if latest and latest.passes_audit:
                    console.print(f"  [cyan]✓ Skeptic Audit [Round {round_num}]: Approved claims against SEC/Market data.[/cyan]")
                else:
                    console.print(f"  [yellow]⚠ Skeptic Audit [Round {round_num}]: Rejected unsupported claims. Triggered revision.[/yellow]")
            elif node_name == "synthesize_memo":
                final_memo = node_state.get("final_memo")

    if final_memo:
        console.print(
            Panel(
                f"[bold]Verdict:[/bold] {final_memo.verdict} | [bold]Conviction:[/bold] {final_memo.conviction_score*100:.1f}%\n"
                f"[bold]Primary Catalyst:[/bold] {final_memo.primary_catalyst}\n"
                f"[bold]Primary Risk:[/bold] {final_memo.primary_risk}\n\n"
                f"{final_memo.synthesis_memo}",
                title=f"[bold green]Autonomous Investigation Memo: {ticker}[/bold green]",
                border_style="green"
            )
        )


def main():
    render_sentinel_banner()
    # Sensitive settings: 1.5x volume surge or 1.8 std deviations
    sentinel = MarketSentinel(volume_threshold=1.5, z_score_threshold=1.8)

    table = Table(title="Sentinel Active Watchlist", box=box.ROUNDED)
    table.add_column("Monitored Ticker", style="bold cyan")
    table.add_column("Status", style="green")
    for t in WATCHLIST:
        table.add_row(t, "Scanning metrics & volatility")
    console.print(table)

    console.print("\n[dim]Press Ctrl+C to terminate Sentinel Daemon.[/dim]\n")

    try:
        while True:
            console.print(f"[dim]Checking watchlist for market anomalies at {time.strftime('%H:%M:%S')}...[/dim]")
            
            for ticker in WATCHLIST:
                result = sentinel.scan_ticker(ticker)
                if result.get("is_anomaly"):
                    run_autonomous_audit(ticker, result)
                else:
                    console.print(f"  [dim]• {ticker}: Normal (Return: {result.get('latest_return_pct')}%, Vol Ratio: {result.get('volume_ratio')}x)[/dim]")

            console.print("[dim]Cycle complete. Sleeping for 60 seconds before next scan...[/dim]\n")
            time.sleep(60)

    except KeyboardInterrupt:
        console.print("\n[yellow]Sentinel Daemon gracefully stopped by user.[/yellow]")


if __name__ == "__main__":
    main()