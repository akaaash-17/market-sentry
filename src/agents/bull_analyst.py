"""
Bullish Growth Analyst Node.
Constructs an aggressive, quantitative upside case grounded strictly in market metrics.
"""
from langchain_ollama import ChatOllama
from config.settings import settings
from src.state import MarketGraphState, AgentThesis


def bull_analyst_node(state: MarketGraphState) -> dict:
    """
    Evaluates market fundamentals and generates a structured Bull thesis.
    """
    llm = ChatOllama(
        model=settings.OLLAMA_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=settings.TEMPERATURE,
        format="json"
    )
    
    # Bind the Pydantic schema for structured output
    structured_llm = llm.with_structured_output(AgentThesis)

    system_prompt = (
        "You are an elite quantitative Wall Street Growth Analyst. "
        "Your role is to build an unapologetic, data-backed Bull Case for the asset. "
        "CRITICAL RULES:\n"
        "1. Every single point MUST cite an exact number or metric from the Market Snapshot (e.g. forward P/E, revenue growth, margin).\n"
        "2. Do NOT invent numbers or use vague assertions like 'strong demand'.\n"
        "3. Output must conform strictly to the AgentThesis schema with stance='BULL'."
    )

    user_content = (
        f"Ticker: {state['ticker']}\n\n"
        f"Market Snapshot Data:\n{state['raw_market_data']}\n\n"
        f"Audit History / Prior Feedback:\n{state.get('audit_history', [])}\n\n"
        "Produce the structured Bull thesis now."
    )

    response: AgentThesis = structured_llm.invoke([
        ("system", system_prompt),
        ("user", user_content)
    ])

    return {"bull_thesis": response}