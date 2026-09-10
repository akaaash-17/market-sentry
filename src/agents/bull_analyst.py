"""
Autonomous Bull Analyst Node.
Uses tool-calling to fetch fundamentals and constructs an evidence-grounded upside thesis.
"""
from langchain_ollama import ChatOllama
from config.settings import settings
from src.state import MarketGraphState, AgentThesis
from src.tools.market_feed import get_valuation_multiples, get_financial_health, get_market_consensus


def bull_analyst_node(state: MarketGraphState) -> dict:
    """
    Autonomous agent node: binds tools, fetches metrics, and outputs a structured thesis.
    """
    ticker = state["ticker"]
    
    # 1. Provide dedicated tools to the agent
    tools = [get_valuation_multiples, get_financial_health, get_market_consensus]
    
    # Gather evidence using tool invocations
    val_data = get_valuation_multiples.invoke({"ticker": ticker})
    health_data = get_financial_health.invoke({"ticker": ticker})
    consensus_data = get_market_consensus.invoke({"ticker": ticker})

    combined_evidence = f"Valuation: {val_data}\nHealth: {health_data}\nConsensus: {consensus_data}"

    llm = ChatOllama(
        model=settings.OLLAMA_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=settings.TEMPERATURE,
        format="json"
    )
    
    structured_llm = llm.with_structured_output(AgentThesis)

    system_prompt = (
        "You are an elite quantitative Growth Analyst. "
        "Formulate a structured Bull Case strictly supported by empirical metrics from the collected data.\n"
        "RULES:\n"
        "1. Every point must cite an exact metric or percentage (e.g. forward P/E, revenue growth, gross margin).\n"
        "2. Do NOT hallucinate metrics not present in the evidence.\n"
        "3. Output strictly conforms to the AgentThesis schema with stance='BULL'."
    )

    user_content = (
        f"Ticker: {ticker}\n\n"
        f"Autonomous Tool Findings:\n{combined_evidence}\n\n"
        f"Prior Audit Feedback (if any):\n{state.get('audit_history', [])}\n\n"
        "Produce the structured Bull thesis."
    )

    response: AgentThesis = structured_llm.invoke([
        ("system", system_prompt),
        ("user", user_content)
    ])

    return {
        "bull_thesis": response,
        "raw_market_data": combined_evidence
    }