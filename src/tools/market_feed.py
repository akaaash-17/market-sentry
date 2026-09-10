"""
Market feed tool using yfinance for zero-cost live metrics, valuation, and news.
"""
import json
from typing import Dict, Any
import yfinance as yf
from langchain_core.tools import tool


def _safe_format(val: Any, prefix: str = "", suffix: str = "") -> str:
    """Safely formats nullable financial metrics."""
    if val is None or val == "N/A":
        return "N/A"
    if isinstance(val, (int, float)):
        return f"{prefix}{val:,.2f}{suffix}"
    return f"{prefix}{val}{suffix}"


@tool
def fetch_market_snapshot(ticker: str) -> str:
    """
    Fetches real-time market quote, fundamental valuation ratios, balance sheet health,
    and recent headlines for a given equity ticker.
    """
    try:
        stock = yf.Ticker(ticker.strip().upper())
        info = stock.info

        # Extract essential metrics
        current_price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose")
        market_cap = info.get("marketCap")
        pe_forward = info.get("forwardPE")
        trailing_pe = info.get("trailingPE")
        peg_ratio = info.get("pegRatio")
        price_to_sales = info.get("priceToSalesTrailing12Months")
        debt_to_equity = info.get("debtToEquity")
        free_cashflow = info.get("freeCashflow")
        rev_growth = info.get("revenueGrowth")
        gross_margins = info.get("grossMargins")
        target_mean_price = info.get("targetMeanPrice")
        recommendation_key = info.get("recommendationKey")

        # Parse recent news headlines
        headlines = []
        raw_news = getattr(stock, "news", []) or []
        for item in raw_news[:5]:
            title = item.get("title")
            publisher = item.get("publisher")
            if title:
                headlines.append(f"- [{publisher}] {title}" if publisher else f"- {title}")

        snapshot: Dict[str, Any] = {
            "ticker": ticker.upper(),
            "company_name": info.get("shortName") or info.get("longName") or ticker.upper(),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "price_metrics": {
                "current_price": _safe_format(current_price, prefix="$"),
                "analyst_mean_target": _safe_format(target_mean_price, prefix="$"),
                "market_cap": _safe_format(market_cap, prefix="$"),
                "consensus_rating": recommendation_key or "N/A",
            },
            "valuation_multiples": {
                "forward_pe": _safe_format(pe_forward),
                "trailing_pe": _safe_format(trailing_pe),
                "peg_ratio": _safe_format(peg_ratio),
                "price_to_sales": _safe_format(price_to_sales),
            },
            "financial_health": {
                "debt_to_equity": _safe_format(debt_to_equity, suffix="%"),
                "revenue_growth_yoy": _safe_format(rev_growth * 100 if isinstance(rev_growth, (int, float)) else None, suffix="%"),
                "gross_margin": _safe_format(gross_margins * 100 if isinstance(gross_margins, (int, float)) else None, suffix="%"),
                "free_cashflow": _safe_format(free_cashflow, prefix="$"),
            },
            "recent_headlines": headlines if headlines else ["No recent headlines available."]
        }

        return json.dumps(snapshot, indent=2)

    except Exception as e:
        return json.dumps({
            "ticker": ticker.upper(),
            "error": f"Failed to retrieve market snapshot: {str(e)}"
        })