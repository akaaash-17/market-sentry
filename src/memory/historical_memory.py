"""
Historical Event Memory Module using ChromaDB and nomic-embed-text via Ollama.
Enables agents to retrieve analog historical market events (e.g., prior supply shocks, guidance cuts).
"""
from typing import List, Dict, Any
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from config.settings import settings


def get_vector_store() -> Chroma:
    """Initializes or connects to the local persistent Chroma vector store."""
    embeddings = OllamaEmbeddings(
        model=settings.EMBEDDING_MODEL,
        base_url=settings.OLLAMA_BASE_URL
    )
    return Chroma(
        collection_name="market_historical_events",
        embedding_function=embeddings,
        persist_directory=settings.VECTOR_DB_DIR
    )


def seed_baseline_market_events():
    """
    Seeds baseline institutional historical market precedents into ChromaDB.
    Runs idempotently (checks existing document count before inserting).
    """
    store = get_vector_store()
    existing = store.get()
    if existing and len(existing.get("ids", [])) > 0:
        return  # Already seeded

    seed_events = [
        Document(
            page_content="NVDA FY24 Q3 Guidance Surge: Data center revenue accelerated +279% YoY on Hopper architecture demand. Forward multiples expanded despite supply constraints.",
            metadata={"ticker": "NVDA", "event_type": "EARNINGS_SURGE", "verdict_outcome": "OVERWEIGHT", "year": "2023"}
        ),
        Document(
            page_content="AAPL Supply Chain Bottleneck: Factory shutdowns and foreign vendor concentration caused delivery delays for flagship devices. Gross margins compressed by 140 bps.",
            metadata={"ticker": "AAPL", "event_type": "SUPPLY_CHAIN_SHOCK", "verdict_outcome": "NEUTRAL", "year": "2022"}
        ),
        Document(
            page_content="TSLA Price Cutting Cycle: Automotive gross margins dropped from 27% to 17% after consecutive price reductions to stimulate volume, causing forward P/E de-rating.",
            metadata={"ticker": "TSLA", "event_type": "MARGIN_COMPRESSION", "verdict_outcome": "UNDERWEIGHT", "year": "2023"}
        ),
        Document(
            page_content="MSFT Cloud & AI Capex Spike: Azure revenue growth stabilized at 29% while capital expenditures rose 55% for AI infrastructure buildout. Free cash flow conversion remained resilient.",
            metadata={"ticker": "MSFT", "event_type": "CAPEX_EXPANSION", "verdict_outcome": "OVERWEIGHT", "year": "2024"}
        )
    ]

    store.add_documents(seed_events)


def query_analogous_events(query_text: str, k: int = 2) -> List[Dict[str, Any]]:
    """Retrieves top-k semantically similar historical events based on current anomaly text."""
    store = get_vector_store()
    results = store.similarity_search_with_score(query_text, k=k)

    analogues = []
    for doc, score in results:
        analogues.append({
            "event_summary": doc.page_content,
            "metadata": doc.metadata,
            "distance_score": round(float(score), 4)
        })
    return analogues


def record_investigated_event(ticker: str, trigger_summary: str, final_verdict: str, rationale: str):
    """Persists a completed MarketSentry investigation into ChromaDB for future queries."""
    store = get_vector_store()
    doc = Document(
        page_content=f"{ticker} Investigation: {trigger_summary}. Outcome: {rationale[:400]}",
        metadata={"ticker": ticker, "verdict": final_verdict, "event_type": "INVESTIGATED_ANOMALY"}
    )
    store.add_documents([doc])