"""
MarketSentry - Interactive Financial Intelligence Dashboard
Zero-cost, local multi-agent LangGraph application.
"""
import streamlit as st
import uuid
from src.graph import build_market_sentry_graph

st.set_page_config(
    page_title="MarketSentry | Multi-Agent Graph",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for an institutional terminal look
st.markdown("""
<style>
    .main { background-color: #0b0f19; }
    .stMetric { background-color: #161f30; padding: 15px; border-radius: 8px; border: 1px solid #22324d; }
    .badge-bull { background-color: #064e3b; color: #34d399; padding: 4px 10px; border-radius: 6px; font-weight: bold; }
    .badge-bear { background-color: #7f1d1d; color: #f87171; padding: 4px 10px; border-radius: 6px; font-weight: bold; }
    .badge-memo { background-color: #1e3a8a; color: #60a5fa; padding: 4px 10px; border-radius: 6px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# App Header
st.title("🛡️ MarketSentry")
st.caption("Autonomous Adversarial Market Intelligence Graph • 100% Local Inference • SEC EDGAR Grounded")

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Execution Controls")
    ticker_input = st.text_input("Equity Ticker Symbol", value="NVDA").upper().strip()
    run_button = st.button("Run Adversarial Audit", type="primary", use_container_width=True)
    
    st.markdown("---")
    st.markdown("""
    **Graph Architecture:**
    - `Ingestion`: Live `yfinance` + SEC EDGAR 10-K
    - `Parallel Nodes`: Bull Growth vs. Bear Short
    - `Reflection Loop`: Skeptic Fact-Checker Audit
    - `Synthesis`: Chief Investment Officer Memo
    """)

if run_button and ticker_input:
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    initial_state = {"ticker": ticker_input}

    # Layout Containers
    status_container = st.status(f"Executing MarketSentry Graph for {ticker_input}...", expanded=True)
    
    app = build_market_sentry_graph()
    
    # Placeholders for data
    final_state = {}

    for step_output in app.stream(initial_state, config=config):
        for node_name, node_state in step_output.items():
            if node_name == "ingestion":
                status_container.write(f"✓ Data Ingestion: Real-time fundamentals & SEC Item 1A Risk Factors parsed.")
            elif node_name == "bull_analyst":
                status_container.write(f"✓ Bull Analyst: Growth thesis formulated with empirical metrics.")
                final_state["bull_thesis"] = node_state.get("bull_thesis")
            elif node_name == "bear_analyst":
                status_container.write(f"✓ Bear Analyst: Forensic risk factors and downside vulnerabilities modeled.")
                final_state["bear_thesis"] = node_state.get("bear_thesis")
            elif node_name == "audit_thesis":
                audits = node_state.get("audit_history", [])
                latest = audits[-1] if audits else None
                round_num = node_state.get("audit_round", 1)
                passed = latest.passes_audit if latest else False
                if passed:
                    status_container.write(f"✓ Skeptic Arbiter [Round {round_num}]: Audit PASSED. Zero unverified metrics.")
                else:
                    status_container.write(f"⚠ Skeptic Arbiter [Round {round_num}]: CHALLENGED. Cycling reflection loop.")
                final_state["audit_history"] = audits
            elif node_name == "synthesize_memo":
                status_container.write(f"✓ Synthesis: Final institutional trade allocation compiled.")
                final_state["final_memo"] = node_state.get("final_memo")

    status_container.update(label=f"Audit Complete for {ticker_input}", state="complete", expanded=False)

    # Display Institutional Memo
    memo = final_state.get("final_memo")
    if memo:
        st.subheader("🏛️ Institutional Allocation Memo")
        col1, col2, col3 = st.columns(3)
        col1.metric("Verdict", memo.verdict)
        col2.metric("Conviction Score", f"{memo.conviction_score * 100:.1f}%")
        col3.metric("Target Asset", memo.ticker)

        c1, c2 = st.columns(2)
        with c1:
            st.success(f"**Primary Growth Catalyst:**\n\n{memo.primary_catalyst}")
        with c2:
            st.error(f"**Primary Risk Vector:**\n\n{memo.primary_risk}")

        st.info(f"**CIO Executive Synthesis:**\n\n{memo.synthesis_memo}")

    # Tabs for Dialectic Debate Analysis
    tab_bull, tab_bear, tab_audit = st.tabs(["🟢 Bullish Case", "🔴 Bearish Case", "🔍 Audit Trail"])

    with tab_bull:
        bull = final_state.get("bull_thesis")
        if bull:
            st.markdown(f"**Thesis:** {bull.summary}")
            points_data = [
                {"Claim": p.point, "Metric / Citation": p.metric_or_citation, "Confidence": f"{p.confidence_score*100:.0f}%"}
                for p in bull.key_points
            ]
            st.dataframe(points_data, use_container_width=True)

    with tab_bear:
        bear = final_state.get("bear_thesis")
        if bear:
            st.markdown(f"**Downside Vulnerabilities:** {bear.summary}")
            points_data = [
                {"Risk Vector": p.point, "Citation / Filing Excerpt": p.metric_or_citation, "Confidence": f"{p.confidence_score*100:.0f}%"}
                for p in bear.key_points
            ]
            st.dataframe(points_data, use_container_width=True)

    with tab_audit:
        audits = final_state.get("audit_history", [])
        if audits:
            for idx, audit in enumerate(audits, 1):
                status_icon = "✅ Passed" if audit.passes_audit else "❌ Challenged"
                st.markdown(f"#### Audit Iteration {idx}: {status_icon}")
                if audit.unsubstantiated_claims:
                    st.write("**Flagged Claims for Revision:**")
                    for claim in audit.unsubstantiated_claims:
                        st.markdown(f"- {claim}")
                else:
                    st.write("All claims verified against SEC Item 1A and market feed snapshots.")