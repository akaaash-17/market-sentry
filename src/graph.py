"""
LangGraph orchestrator for MarketSentry.
Implements parallel node execution, conditional reflection loops, and state persistence.
"""
from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from config.settings import settings
from src.state import MarketGraphState
from src.tools.market_feed import fetch_market_snapshot
from src.tools.sec_edgar import fetch_sec_risk_disclosures
from src.agents.bull_analyst import bull_analyst_node
from src.agents.bear_analyst import bear_analyst_node
from src.agents.skeptic_arbiter import audit_thesis_node, synthesize_memo_node


# ---------------------------------------------------------------------------
# Node: Data Ingestion & Normalization
# ---------------------------------------------------------------------------

def ingestion_node(state: MarketGraphState) -> dict:
    """
    Parallel gateway node: extracts market metrics and SEC filings,
    initializing the shared state for downstream debate nodes.
    """
    ticker = state["ticker"].strip().upper()
    
    market_snapshot_json = fetch_market_snapshot.invoke({"ticker": ticker})
    sec_risk_json = fetch_sec_risk_disclosures.invoke({"ticker": ticker})

    return {
        "ticker": ticker,
        "raw_market_data": market_snapshot_json,
        "raw_sec_data": sec_risk_json,
        "audit_round": 0,
        "is_audit_approved": False,
        "audit_history": []
    }


# ---------------------------------------------------------------------------
# Conditional Edge Router
# ---------------------------------------------------------------------------

def audit_router(state: MarketGraphState) -> Literal["synthesize_memo", "bull_analyst"]:
    """
    Cyclic router: evaluates whether the audit passed or max audit loops were reached.
    If audit fails, it routes back to bull/bear nodes for re-grounding.
    If approved, it advances to final memo synthesis.
    """
    if state.get("is_audit_approved", False):
        return "synthesize_memo"
    
    # If the audit failed and rounds remain, cycle back for revision
    return "bull_analyst"


# ---------------------------------------------------------------------------
# Graph Construction & Compilation
# ---------------------------------------------------------------------------

def build_market_sentry_graph():
    """
    Constructs the compiled LangGraph workflow with in-memory persistence.
    """
    workflow = StateGraph(MarketGraphState)

    # 1. Register all nodes
    workflow.add_node("ingestion", ingestion_node)
    workflow.add_node("bull_analyst", bull_analyst_node)
    workflow.add_node("bear_analyst", bear_analyst_node)
    workflow.add_node("audit_thesis", audit_thesis_node)
    workflow.add_node("synthesize_memo", synthesize_memo_node)

    # 2. Define edge connections
    workflow.set_entry_point("ingestion")

    # Ingestion forks in parallel to Bull and Bear analysts
    workflow.add_edge("ingestion", "bull_analyst")
    workflow.add_edge("ingestion", "bear_analyst")

    # Both analysts join into the Skeptic Auditor
    workflow.add_edge("bull_analyst", "audit_thesis")
    workflow.add_edge("bear_analyst", "audit_thesis")

    # Conditional branching from Audit: continue loop or advance to synthesis
    workflow.add_conditional_edges(
        "audit_thesis",
        audit_router,
        {
            "synthesize_memo": "synthesize_memo",
            "bull_analyst": "bull_analyst"
        }
    )

    # Synthesis completes the graph
    workflow.add_edge("synthesize_memo", END)

    # 3. Attach in-memory checkpointer for thread isolation and state history
    checkpointer = MemorySaver()

    # Compile the graph
    app = workflow.compile(checkpointer=checkpointer)
    return app