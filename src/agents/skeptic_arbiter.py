"""
Skeptic Arbiter Node.
Performs fact-checking audit on both theses and synthesizes the final trade memo.
"""
import json
from langchain_ollama import ChatOllama
from config.settings import settings
from src.state import MarketGraphState, AuditCritique, FinalInvestmentMemo


def audit_thesis_node(state: MarketGraphState) -> dict:
    """
    Cross-checks Bull and Bear points against ground-truth data.
    If claims hallucinate metrics, rejects the audit and triggers loop revision.
    """
    llm = ChatOllama(
        model=settings.OLLAMA_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=0.0,
        format="json"
    )

    current_round = state.get("audit_round", 0) + 1
    
    bull_summary = state["bull_thesis"].model_dump_json() if state.get("bull_thesis") else "{}"
    bear_summary = state["bear_thesis"].model_dump_json() if state.get("bear_thesis") else "{}"

    system_prompt = (
        "You are an impartial Chief Compliance and Fact-Checking Officer. "
        "Inspect the Bull and Bear claims. Verify whether their cited numbers match the ground-truth data.\n"
        "If an agent cited a number that DOES NOT exist in the provided snapshot or SEC text, "
        "flag it in unsubstantiated_claims and mark passes_audit as False.\n"
        "If all claims are verified by the data, mark passes_audit as True."
    )

    user_content = (
        f"Ground Truth Market Data:\n{state['raw_market_data']}\n\n"
        f"Ground Truth SEC Data:\n{state['raw_sec_data']}\n\n"
        f"Bull Thesis Under Review:\n{bull_summary}\n\n"
        f"Bear Thesis Under Review:\n{bear_summary}\n\n"
        "Perform audit verification for the Bull stance first."
    )

    structured_llm = llm.with_structured_output(AuditCritique)
    critique: AuditCritique = structured_llm.invoke([
        ("system", system_prompt),
        ("user", user_content)
    ])

    # If maximum rounds reached, approve to avoid an infinite loop
    approved = critique.passes_audit or (current_round >= settings.MAX_AUDIT_ROUNDS)

    return {
        "audit_history": [critique],
        "audit_round": current_round,
        "is_audit_approved": approved
    }


def synthesize_memo_node(state: MarketGraphState) -> dict:
    """
    Once the audit is passed, synthesize both theses into an institutional memo.
    """
    llm = ChatOllama(
        model=settings.OLLAMA_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=settings.TEMPERATURE,
        format="json"
    )
    
    structured_llm = llm.with_structured_output(FinalInvestmentMemo)

    system_prompt = (
        "You are the Chief Investment Officer (CIO) of a quantitative multi-strategy fund. "
        "Review the verified Bull and Bear debates to deliver an actionable Investment Memo. "
        "Choose a verdict: 'OVERWEIGHT', 'NEUTRAL', or 'UNDERWEIGHT'. "
        "Base conviction on the weight of verified empirical evidence."
    )

    user_content = (
        f"Ticker: {state['ticker']}\n\n"
        f"Verified Bull Thesis:\n{state['bull_thesis'].model_dump_json() if state.get('bull_thesis') else ''}\n\n"
        f"Verified Bear Thesis:\n{state['bear_thesis'].model_dump_json() if state.get('bear_thesis') else ''}\n\n"
        "Generate the complete FinalInvestmentMemo."
    )

    memo: FinalInvestmentMemo = structured_llm.invoke([
        ("system", system_prompt),
        ("user", user_content)
    ])

    return {"final_memo": memo}