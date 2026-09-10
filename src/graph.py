"""
LangGraph orchestrator for MarketSentry (v0.2 Autonomous Architecture).
Implements autonomous agent tool-calling, hybrid deterministic auditing, and persistent SQLite checkpointing.
"""
import sqlite3
from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from config.settings import settings
from src.state import MarketGraphState
from src.agents.bull_analyst import bull_analyst_node
from src.agents.bear_analyst import bear_analyst_node
from src.agents.skeptic_arbiter import audit_thesis_node, synthesize_memo_node


def init_node(state: MarketGraphState) -> dict:
    """Initializes execution state and thread variables."""
    return {
        "ticker": state["ticker"].strip().upper(),
        "audit_round": 0,
        "is_audit_approved": False,
        "audit_history": []
    }


def audit_router(state: MarketGraphState) -> Literal["synthesize_memo", "bull_analyst"]:
    """Routes execution based on verification and iteration limits."""
    if state.get("is_audit_approved", False):
        return "synthesize_memo"
    return "bull_analyst"


def build_market_sentry_graph():
    """Compiles the state graph with SQLite persistence."""
    workflow = StateGraph(MarketGraphState)

    # 1. Register nodes
    workflow.add_node("init", init_node)
    workflow.add_node("bull_analyst", bull_analyst_node)
    workflow.add_node("bear_analyst", bear_analyst_node)
    workflow.add_node("audit_thesis", audit_thesis_node)
    workflow.add_node("synthesize_memo", synthesize_memo_node)

    # 2. Wire graph edges
    workflow.set_entry_point("init")

    # Parallel dispatch to autonomous agents
    workflow.add_edge("init", "bull_analyst")
    workflow.add_edge("init", "bear_analyst")

    # Join into hybrid auditor
    workflow.add_edge("bull_analyst", "audit_thesis")
    workflow.add_edge("bear_analyst", "audit_thesis")

    # Conditional reflection edge
    workflow.add_conditional_edges(
        "audit_thesis",
        audit_router,
        {
            "synthesize_memo": "synthesize_memo",
            "bull_analyst": "bull_analyst"
        }
    )

    workflow.add_edge("synthesize_memo", END)

    # Persistent SQLite Checkpointer
    conn = sqlite3.connect(settings.CHECKPOINT_DB_PATH, check_same_thread=False)
    checkpointer = SqliteSaver(conn)

    return workflow.compile(checkpointer=checkpointer)