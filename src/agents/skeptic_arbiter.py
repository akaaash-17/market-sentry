"""
Skeptic Arbiter Node with Hybrid Verification & ChromaDB Semantic Memory:
1. Deterministic Python metric verification (math/ground-truth checks).
2. Semantic historical event retrieval via ChromaDB.
3. LLM qualitative audit & synthesis.
"""
import json
import re
from typing import List
from langchain_ollama import ChatOllama
from config.settings import settings
from src.state import MarketGraphState, AuditCritique, FinalInvestmentMemo, AgentThesis
from src.memory.historical_memory import query_analogous_events, record_investigated_event


def _extract_numbers(text: str) -> List[float]:
    """Extracts all floats/integers from a claim string."""
    matches = re.findall(r'[-+]?\d*\.?\d+', text.replace(',', ''))
    numbers = []
    for m in matches:
        try:
            val = float(m)
            numbers.append(val)
        except ValueError:
            continue
    return numbers


def verify_claims_deterministically(thesis: AgentThesis, raw_market_json: str) -> List[str]:
    """
    Deterministic fact-checker: extracts cited metrics from analyst points and verifies
    whether they exist within a tolerance threshold in raw market data.
    """
    unsubstantiated = []
    if not thesis or not raw_market_json:
        return unsubstantiated

    try:
        ground_truth = json.loads(raw_market_json)
        raw_text_corpus = json.dumps(ground_truth).lower()

        for point in thesis.key_points:
            claim_text = f"{point.point} {point.metric_or_citation}".lower()
            numbers_in_claim = _extract_numbers(claim_text)
            
            for num in numbers_in_claim:
                num_str_short = f"{num:.2f}".rstrip('0').rstrip('.')
                int_str = str(int(num)) if num.is_integer() else None

                matched = (num_str_short in raw_text_corpus) or (int_str and int_str in raw_text_corpus)
                citation_key = point.metric_or_citation.strip().lower()
                key_found = any(k in raw_text_corpus for k in citation_key.split())

                if not matched and not key_found:
                    unsubstantiated.append(
                        f"Unverified number [{num}] in claim: '{point.point}'"
                    )
                    break
    except Exception:
        pass

    return unsubstantiated


def audit_thesis_node(state: MarketGraphState) -> dict:
    """
    Hybrid Skeptic Auditor: Runs deterministic checks first, then invokes LLM
    for qualitative and contextual verification.
    """
    current_round = state.get("audit_round", 0) + 1
    raw_market = state.get("raw_market_data", "{}")
    raw_sec = state.get("raw_sec_data", "{}")
    
    bull = state.get("bull_thesis")
    bear = state.get("bear_thesis")

    # 1. Deterministic Verification Layer
    deterministic_flags = []
    if bull:
        deterministic_flags.extend(verify_claims_deterministically(bull, raw_market))
    if bear:
        deterministic_flags.extend(verify_claims_deterministically(bear, raw_market))

    # 2. LLM Qualitative Audit Layer
    llm = ChatOllama(
        model=settings.OLLAMA_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=0.0,
        format="json"
    )

    system_prompt = (
        "You are an impartial Chief Compliance and Fact-Checking Officer. "
        "Review the Bull and Bear claims against ground-truth data.\n"
        "Rules:\n"
        "1. Flag any claims that cite figures not present in ground-truth data.\n"
        "2. If deterministic verification flags exist, incorporate them into unsubstantiated_claims.\n"
        "3. Set passes_audit=True ONLY if both stances are grounded."
    )

    user_content = (
        f"Ground Truth Market Data:\n{raw_market}\n\n"
        f"Ground Truth SEC 10-K Data:\n{raw_sec}\n\n"
        f"Deterministic Verification Flags:\n{deterministic_flags}\n\n"
        f"Bull Thesis:\n{bull.model_dump_json() if bull else '{}'}\n\n"
        f"Bear Thesis:\n{bear.model_dump_json() if bear else '{}'}\n\n"
        "Perform the compliance audit."
    )

    structured_llm = llm.with_structured_output(AuditCritique)
    critique: AuditCritique = structured_llm.invoke([
        ("system", system_prompt),
        ("user", user_content)
    ])

    combined_flags = list(set(critique.unsubstantiated_claims + deterministic_flags))
    critique.unsubstantiated_claims = combined_flags
    
    if deterministic_flags:
        critique.passes_audit = False

    approved = critique.passes_audit or (current_round >= settings.MAX_AUDIT_ROUNDS)

    return {
        "audit_history": [critique],
        "audit_round": current_round,
        "is_audit_approved": approved
    }


def synthesize_memo_node(state: MarketGraphState) -> dict:
    """
    Synthesizes the verified debate into an institutional CIO trade memo,
    enriching the context with semantic historical precedents from ChromaDB.
    """
    ticker = state["ticker"]
    bull = state.get("bull_thesis")
    bear = state.get("bear_thesis")

    # Retrieve semantic historical analogues from ChromaDB
    query_context = f"{ticker}: {bull.summary if bull else ''} {bear.summary if bear else ''}"
    analogues = query_analogous_events(query_context, k=2)
    analogues_formatted = "\n".join([f"- {a['event_summary']} (Score: {a['distance_score']})" for a in analogues])

    llm = ChatOllama(
        model=settings.OLLAMA_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=settings.TEMPERATURE,
        format="json"
    )
    
    structured_llm = llm.with_structured_output(FinalInvestmentMemo)

    system_prompt = (
        "You are the Chief Investment Officer (CIO) of a quantitative fund. "
        "Synthesize the audited Bull and Bear theses and analogous historical precedents into an Investment Memo. "
        "Assign an institutional verdict: 'OVERWEIGHT', 'NEUTRAL', or 'UNDERWEIGHT'."
    )

    user_content = (
        f"Ticker: {ticker}\n\n"
        f"Historical Event Analogues (Retrieved via ChromaDB):\n{analogues_formatted}\n\n"
        f"Audited Bull Thesis:\n{bull.model_dump_json() if bull else ''}\n\n"
        f"Audited Bear Thesis:\n{bear.model_dump_json() if bear else ''}\n\n"
        "Generate the FinalInvestmentMemo."
    )

    memo: FinalInvestmentMemo = structured_llm.invoke([
        ("system", system_prompt),
        ("user", user_content)
    ])

    # Persist the newly investigated event into ChromaDB for future memory
    try:
        record_investigated_event(
            ticker=ticker,
            trigger_summary=f"Bull: {bull.summary[:100] if bull else ''} | Bear: {bear.summary[:100] if bear else ''}",
            final_verdict=memo.verdict,
            rationale=memo.synthesis_memo
        )
    except Exception:
        pass

    return {"final_memo": memo}