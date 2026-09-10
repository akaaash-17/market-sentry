"""
Bearish Risk Officer / Short-Seller Node.
Constructs a defensive downside case grounded in SEC risk disclosures and valuation multiples.
"""
from langchain_ollama import ChatOllama
from config.settings import settings
from src.state import MarketGraphState, AgentThesis


def bear_analyst_node(state: MarketGraphState) -> dict:
    """
    Evaluates SEC filings and multiples to generate a structured Bear thesis.
    """
    llm = ChatOllama(
        model=settings.OLLAMA_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=settings.TEMPERATURE,
        format="json"
    )
    
    structured_llm = llm.with_structured_output(AgentThesis)

    system_prompt = (
        "You are a forensic hedge fund short-seller and risk auditor. "
        "Your role is to dismantle the company's valuation and uncover vulnerability vectors. "
        "CRITICAL RULES:\n"
        "1. Focus on Item 1A Risk Factors, debt ratios, margin sustainability, or high multiples.\n"
        "2. Every point MUST cite an exact number, multiple, or direct phrase from the SEC excerpt.\n"
        "3. Do NOT make generic assumptions. Every claim must cite the provided data.\n"
        "4. Output must conform strictly to the AgentThesis schema with stance='BEAR'."
    )

    user_content = (
        f"Ticker: {state['ticker']}\n\n"
        f"Market Snapshot Data:\n{state['raw_market_data']}\n\n"
        f"SEC 10-K Risk Disclosures:\n{state['raw_sec_data']}\n\n"
        f"Audit History / Prior Feedback:\n{state.get('audit_history', [])}\n\n"
        "Produce the structured Bear thesis now."
    )

    response: AgentThesis = structured_llm.invoke([
        ("system", system_prompt),
        ("user", user_content)
    ])

    return {"bear_thesis": response}