"""
MarketSentry - Interactive Financial Intelligence & Sentinel Dashboard
Zero-cost, local multi-agent LangGraph application with ChromaDB Semantic Memory.
"""
import streamlit as st
import uuid
import pandas as pd
from src.graph import build_market_sentry_graph
from src.tools.anomaly_detector import MarketSentinel
from src.memory.historical_memory import seed_baseline_market_events, query_analogous_events

# Seed baseline events once per session
seed_baseline_market_events()

st.set_page_config(
    page_title="MarketSentry | Autonomous Agent Graph",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main { background-color: #0b0f19; }
    .stMetric { background-color: #161f30; padding: 15px; border-radius: 8px; border: 1px solid #22324d; }
    .memory-box { background-color: #1a2333; padding: 12px; border-radius: 6px; border-left: 4px solid #38bdf8; margin-bottom: 8px; }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ MarketSentry")
st.caption("Autonomous Adversarial Market Intelligence Graph • ChromaDB Semantic Memory • 100% Local Inference")

mode = st.sidebar.radio("Navigation Mode", ["🎯 Deep Dive Audit", "📡 Sentinel Anomaly Scanner", "🧠 ChromaDB Historical Precedents"])

WATCHLIST = ["NVDA", "TSLA", "AAPL", "MSFT", "GOOGL", "AMZN", "AMD"]

# ---------------------------------------------------------------------------
# MODE 1: DEEP DIVE AUDIT
# ---------------------------------------------------------------------------
if mode == "🎯 Deep Dive Audit":
    with st.sidebar:
        st.header("⚙️ Audit Controls")
        ticker_input = st.text_input("Equity Ticker", value="NVDA").upper().strip()
        run_button = st.button("Run Adversarial Audit", type="primary", use_container_width=True)

    if run_button and ticker_input:
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        initial_state = {"ticker": ticker_input}

        status_container = st.status(f"Executing MarketSentry Graph for {ticker_input}...", expanded=True)
        app = build_market_sentry_graph()
        final_state = {}

        for step_output in app.stream(initial_state, config=config):
            for node_name, node_state in step_output.items():
                if node_name == "init":
                    status_container.write(f"✓ Initialized thread context ({thread_id[:8]})")
                elif node_name == "bull_analyst":
                    status_container.write(f"✓ Bull Analyst: Formulated upside thesis with empirical metrics.")
                    final_state["bull_thesis"] = node_state.get("bull_thesis")
                elif node_name == "bear_analyst":
                    status_container.write(f"✓ Bear Analyst: Isolated forensic downside and SEC 10-K risk disclosures.")
                    final_state["bear_thesis"] = node_state.get("bear_thesis")
                elif node_name == "audit_thesis":
                    audits = node_state.get("audit_history", [])
                    latest = audits[-1] if audits else None
                    round_num = node_state.get("audit_round", 1)
                    if latest and latest.passes_audit:
                        status_container.write(f"✓ Skeptic Arbiter [Round {round_num}]: Audit PASSED.")
                    else:
                        status_container.write(f"⚠ Skeptic Arbiter [Round {round_num}]: CHALLENGED. Triggered reflection loop.")
                    final_state["audit_history"] = audits
                elif node_name == "synthesize_memo":
                    status_container.write(f"✓ CIO Synthesis: Final institutional trade allocation compiled via ChromaDB memory.")
                    final_state["final_memo"] = node_state.get("final_memo")

        status_container.update(label=f"Forensic Audit Complete: {ticker_input}", state="complete", expanded=False)

        memo = final_state.get("final_memo")
        if memo:
            st.subheader(f"🏛️ CIO Allocation Memo: {ticker_input}")
            col1, col2, col3 = st.columns(3)
            col1.metric("Verdict", memo.verdict)
            col2.metric("Conviction Score", f"{memo.conviction_score * 100:.1f}%")
            col3.metric("Target Asset", memo.ticker)

            c1, c2 = st.columns(2)
            with c1:
                st.success(f"**Primary Growth Catalyst:**\n\n{memo.primary_catalyst}")
            with c2:
                st.error(f"**Primary Risk Vector:**\n\n{memo.primary_risk}")

            st.info(f"**CIO Executive Rationale (Grounded in SEC & ChromaDB Precedents):**\n\n{memo.synthesis_memo}")

        tab_bull, tab_bear, tab_memory, tab_audit = st.tabs(["🟢 Bullish Thesis", "🔴 Bearish Thesis", "🧠 Historical Precedents", "🔍 Audit History"])

        with tab_bull:
            bull = final_state.get("bull_thesis")
            if bull:
                st.markdown(f"**Summary:** {bull.summary}")
                st.dataframe([{"Claim": p.point, "Citation / Metric": p.metric_or_citation, "Confidence": f"{p.confidence_score*100:.0f}%"} for p in bull.key_points], use_container_width=True)

        with tab_bear:
            bear = final_state.get("bear_thesis")
            if bear:
                st.markdown(f"**Summary:** {bear.summary}")
                st.dataframe([{"Risk Vector": p.point, "SEC Citation": p.metric_or_citation, "Confidence": f"{p.confidence_score*100:.0f}%"} for p in bear.key_points], use_container_width=True)

        with tab_memory:
            st.markdown("### Semantically Analogous Events Retrieved from ChromaDB")
            retrieved = query_analogous_events(f"{ticker_input} market thesis", k=3)
            for item in retrieved:
                st.markdown(f"""
                <div class="memory-box">
                    <strong>Event:</strong> {item['event_summary']}<br>
                    <small>Metadata: {item['metadata']} | Distance Score: {item['distance_score']}</small>
                </div>
                """, unsafe_allow_html=True)

        with tab_audit:
            audits = final_state.get("audit_history", [])
            for idx, a in enumerate(audits, 1):
                icon = "✅ Passed" if a.passes_audit else "❌ Challenged"
                st.markdown(f"**Round {idx}: {icon}**")
                if a.unsubstantiated_claims:
                    for claim in a.unsubstantiated_claims:
                        st.write(f"- {claim}")

# ---------------------------------------------------------------------------
# MODE 2: SENTINEL SCANNER
# ---------------------------------------------------------------------------
elif mode == "📡 Sentinel Anomaly Scanner":
    st.subheader("📡 Live Watchlist Sentinel Scanner")
    st.caption("Continuously calculates intraday return z-scores and volume surge ratios across benchmark equities.")

    if st.button("Scan Watchlist for Anomalies", type="primary"):
        sentinel = MarketSentinel(volume_threshold=1.5, z_score_threshold=1.8)
        
        results = []
        with st.spinner("Analyzing statistical distributions across watchlist..."):
            for sym in WATCHLIST:
                res = sentinel.scan_ticker(sym)
                results.append(res)

        df = pd.DataFrame(results)
        st.dataframe(df[["ticker", "is_anomaly", "latest_price", "latest_return_pct", "z_score", "volume_ratio"]], use_container_width=True)

        anomalies = [r for r in results if r.get("is_anomaly")]
        if anomalies:
            st.error(f"🚨 {len(anomalies)} Market Anomaly Detected!")
            for anom in anomalies:
                st.markdown(f"**{anom['ticker']} Alerts:**")
                for t in anom.get("triggers", []):
                    st.write(f"- {t}")
        else:
            st.success("✓ All watchlist assets trading within normal volatility distributions.")

# ---------------------------------------------------------------------------
# MODE 3: HISTORICAL PRECEDENTS INSPECTOR
# ---------------------------------------------------------------------------
elif mode == "🧠 ChromaDB Historical Precedents":
    st.subheader("🧠 ChromaDB Semantic Precedents Browser")
    st.caption("Directly query MarketSentry's dense vector index using nomic-embed-text embeddings.")

    query = st.text_input("Semantic Query", value="capex expansion and artificial intelligence infrastructure")
    if st.button("Search Precedents", type="primary"):
        results = query_analogous_events(query, k=4)
        for r in results:
            st.markdown(f"""
            <div class="memory-box">
                <strong>Precedent:</strong> {r['event_summary']}<br>
                <small>Metadata: {r['metadata']} | Cosine Distance: {r['distance_score']}</small>
            </div>
            """, unsafe_allow_html=True)