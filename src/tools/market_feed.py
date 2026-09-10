"""
Granular Market Tools for Autonomous Agent Selection.
Allows Bull and Bear agents to query specific financial subsystems on demand.
"""
import json
from typing import Any
import yfinance as yf
from langchain_core.tools import tool


def _safe_format(val: Any, prefix: str = "", suffix: str = "") -> str:
    if val is None or val == "N/A":
        return "N/A"
    if isinstance(val, (int, float)):
        return f"{prefix}{val:,.2f}{suffix}"
    return f"{prefix}{val}{suffix}"


@tool
def get_valuation_multiples(ticker: str) -> str:
    """Fetches equity valuation ratios: forward P/E, trailing P/E, PEG ratio, and price-to-sales."""
    try:
        info = yf.Ticker(ticker.strip().upper()).info
        return json.dumps({
            "ticker": ticker.upper(),
            "forward_pe": _safe_format(info.get("forwardPE")),
            "trailing_pe": _safe_format(info.get("trailingPE")),
            "peg_ratio": _safe_format(info.get("pegRatio")),
            "price_to_sales": _safe_format(info.get("priceToSalesTrailing12Months"))
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def get_financial_health(ticker: str) -> str:
    """Fetches balance sheet health: debt-to-equity, gross margins, YoY revenue growth, and free cash flow."""
    try:
        info = yf.Ticker(ticker.strip().upper()).info
        rev_growth = info.get("revenueGrowth")
        gross_margins = info.get("grossMargins")
        return json.dumps({
            "ticker": ticker.upper(),
            "debt_to_equity": _safe_format(info.get("debtToEquity"), suffix="%"),
            "revenue_growth_yoy": _safe_format(rev_growth * 100 if isinstance(rev_growth, (int, float)) else None, suffix="%"),
            "gross_margin": _safe_format(gross_margins * 100 if isinstance(gross_margins, (int, float)) else None, suffix="%"),
            "free_cashflow": _safe_format(info.get("freeCashflow"), prefix="$")
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def get_market_consensus(ticker: str) -> str:
    """Fetches price targets, consensus analyst recommendation, and current market cap."""
    try:
        info = yf.Ticker(ticker.strip().upper()).info
        return json.dumps({
            "ticker": ticker.upper(),
            "current_price": _safe_format(info.get("currentPrice") or info.get("regularMarketPrice"), prefix="$"),
            "target_mean_price": _safe_format(info.get("targetMeanPrice"), prefix="$"),
            "market_cap": _safe_format(info.get("marketCap"), prefix="$"),
            "consensus_rating": info.get("recommendationKey", "N/A")
        })
    except Exception as e:
        return json.dumps({"error": str(e)})