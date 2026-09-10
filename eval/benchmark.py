"""
MarketSentry Automated Evaluation Benchmark.
Measures evidence grounding accuracy, loop convergence, latency, and unsupported claim rates.
"""
import os
import sys
import time
import uuid
from typing import List, Dict, Any

# Ensure project root is in sys.path when running from subdirectories
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from src.graph import build_market_sentry_graph
from src.agents.skeptic_arbiter import verify_claims_deterministically

console = Console()

# Curated benchmark assets covering Tech, Automotive, and Large-Cap
BENCHMARK_TICKERS = ["AAPL", "NVDA", "MSFT", "TSLA"]


class BenchmarkSuite:
    def __init__(self, tickers: List[str]):
        self.tickers = tickers
        self.results: List[Dict[str, Any]] = []

    def run_eval(self):
        console.print(
            Panel.fit(
                "[bold cyan]MarketSentry Institutional Evaluation Benchmark[/bold cyan]\n"
                "[dim]Testing Deterministic Grounding • Loop Convergence • Execution Latency[/dim]",
                box=box.DOUBLE,
                border_style="cyan"
            )
        )

        app = build_market_sentry_graph()

        for ticker in self.tickers:
            console.print(f"\n[yellow]▶ Running forensic evaluation on {ticker}...[/yellow]")
            thread_id = str(uuid.uuid4())
            config = {"configurable": {"thread_id": thread_id}}
            initial_state = {"ticker": ticker}

            start_time = time.time()
            final_state = {}

            for step_output in app.stream(initial_state, config=config):
                for node_name, node_state in step_output.items():
                    final_state.update(node_state)

            elapsed_latency = time.time() - start_time

            # Compute Metric 1: Total & Unsupported Claims
            bull = final_state.get("bull_thesis")
            bear = final_state.get("bear_thesis")
            raw_market = final_state.get("raw_market_data", "{}")

            total_claims = 0
            unsupported_claims_count = 0

            if bull:
                total_claims += len(bull.key_points)
                unsupported_claims_count += len(verify_claims_deterministically(bull, raw_market))

            if bear:
                total_claims += len(bear.key_points)
                unsupported_claims_count += len(verify_claims_deterministically(bear, raw_market))

            grounded_claims = max(0, total_claims - unsupported_claims_count)
            grounding_rate = (grounded_claims / total_claims * 100) if total_claims > 0 else 100.0
            unsupported_rate = (unsupported_claims_count / total_claims * 100) if total_claims > 0 else 0.0

            # Compute Metric 2: Audit Rounds
            rounds = final_state.get("audit_round", 1)
            is_approved = final_state.get("is_audit_approved", False)

            # Compute Metric 3: Synthesis Verdict & Conviction
            memo = final_state.get("final_memo")
            verdict = memo.verdict if memo else "N/A"
            conviction = f"{memo.conviction_score * 100:.1f}%" if memo else "N/A"

            entry = {
                "ticker": ticker,
                "latency_sec": round(elapsed_latency, 2),
                "audit_rounds": rounds,
                "total_claims": total_claims,
                "grounding_rate": round(grounding_rate, 1),
                "unsupported_rate": round(unsupported_rate, 1),
                "approved": is_approved,
                "verdict": verdict,
                "conviction": conviction
            }
            self.results.append(entry)
            console.print(f"  [green]✓ Completed {ticker} in {elapsed_latency:.2f}s (Grounding: {grounding_rate:.1f}%, Rounds: {rounds})[/green]")

    def display_metrics(self):
        if not self.results:
            return

        table = Table(title="📊 MarketSentry Benchmark Results Matrix", box=box.ROUNDED, border_style="cyan")
        table.add_column("Ticker", style="bold white", width=8)
        table.add_column("Latency (s)", justify="right", style="dim white", width=12)
        table.add_column("Rounds", justify="center", style="cyan", width=8)
        table.add_column("Claims", justify="center", style="white", width=8)
        table.add_column("Grounding Rate", justify="right", style="green", width=16)
        table.add_column("Unsupported Rate", justify="right", style="red", width=18)
        table.add_column("Final Verdict", style="bold yellow", width=14)
        table.add_column("Conviction", justify="right", style="magenta", width=12)

        total_latency = 0.0
        total_grounding = 0.0
        total_unsupported = 0.0
        total_rounds = 0

        for r in self.results:
            table.add_row(
                r["ticker"],
                f"{r['latency_sec']:.2f}s",
                str(r["audit_rounds"]),
                str(r["total_claims"]),
                f"{r['grounding_rate']:.1f}%",
                f"{r['unsupported_rate']:.1f}%",
                r["verdict"],
                r["conviction"]
            )
            total_latency += r["latency_sec"]
            total_grounding += r["grounding_rate"]
            total_unsupported += r["unsupported_rate"]
            total_rounds += r["audit_rounds"]

        n = len(self.results)
        console.print("\n")
        console.print(table)

        avg_latency = total_latency / n
        avg_grounding = total_grounding / n
        avg_unsupported = total_unsupported / n
        avg_rounds = total_rounds / n

        summary_text = (
            f"[bold cyan]Aggregate System Performance across {n} Assets:[/bold cyan]\n\n"
            f"• [bold white]Average Grounding Accuracy:[/bold white] [bold green]{avg_grounding:.1f}%[/bold green]\n"
            f"• [bold white]Deterministic Hallucination / Unsupported Rate:[/bold white] [bold red]{avg_unsupported:.1f}%[/bold red]\n"
            f"• [bold white]Mean Convergence Iterations:[/bold white] [bold yellow]{avg_rounds:.2f} rounds[/bold yellow]\n"
            f"• [bold white]Mean Execution Latency on Local CPU:[/bold white] [bold white]{avg_latency:.2f}s per asset[/bold white]\n"
        )
        console.print(Panel(summary_text, title="[bold]Evaluation Summary[/bold]", border_style="green", box=box.HEAVY_EDGE))


def main():
    suite = BenchmarkSuite(tickers=BENCHMARK_TICKERS)
    suite.run_eval()
    suite.display_metrics()


if __name__ == "__main__":
    main()