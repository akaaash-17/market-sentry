"""
Autonomous Bear Analyst Node.
Uses tool-calling to fetch SEC Item 1A disclosures and debt health, constructing a downside thesis.
"""
from langchain_ollama import ChatOllama
from config.settings import settings
from src.state import MarketGraphState, AgentThesis
from src.tools.market_feed import get_valuation_multiples, get_financial_health
from src.tools.sec_edgar import fetch_sec_risk_disclosures


def bear_analyst_node(state: MarketGraphState) -> dict:
    """
    Autonomous agent node: binds tools, fetches SEC disclosures and leverage metrics,
    and outputs a structured short thesis.
    """
    ticker = state["ticker"]
    
    # Gather evidence from SEC filings and multiples
    sec_data = fetch_sec_risk_disclosures.invoke({"ticker": ticker})
    health_data = get_financial_health.invoke({"ticker": ticker})
    val_data = get_valuation_multiples.invoke({"ticker": ticker})

    combined_evidence = f"SEC Risks:\n{sec_data}\n\nFinancial Health:\n{health_data}\n\nValuation:\n{val_data}"

    llm = ChatOllama(
        model=settings.OLLAMA_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=settings.TEMPERATURE,
        format="json"
    )
    
    structured_llm = llm.with_structured_output(AgentThesis)

    system_prompt = (
        "You are a forensic hedge fund short-seller and risk auditor. "
        "Formulate a structured Bear Case strictly citing SEC 10-K risk factors, high multiples, or debt drag.\n"
        "RULES:\n"
        "1. Every point must cite an exact number, multiple, or direct phrase from the SEC excerpt.\n"
        "2. Do NOT make generic assumptions.\n"
        "3. Output strictly conforms to the AgentThesis schema with stance='BEAR'."
    )

    user_content = (
        f"Ticker: {ticker}\n\n"
        f"Autonomous Tool Findings:\n{combined_evidence}\n\n"
        f"Prior Audit Feedback (if any):\n{state.get('audit_history', [])}\n\n"
        "Produce the structured Bear thesis."
    )

    response: AgentThesis = structured_llm.invoke([
        ("system", system_prompt),
        ("user", user_content)
    ])

    return {
        "bear_thesis": response,
        "raw_sec_data": sec_data
    }