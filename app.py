"""
MarketSentry - Institutional Market Analytics & Anomaly Terminal
Modern neutral dark design system modeled after high-density fintech dashboards.
"""
import streamlit as st
import uuid
import pandas as pd

from src.graph import build_market_sentry_graph
from src.tools.anomaly_detector import MarketSentinel
from src.tools.visualizer import generate_anomaly_chart, generate_dialectic_comparison_chart
from src.memory.historical_memory import seed_baseline_market_events, query_analogous_events

seed_baseline_market_events()

st.set_page_config(
    page_title="MarketSentry Analytics",
    page_icon="▪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------------------------
# High-Density Fintech CSS Architecture
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    header[data-testid="stHeader"], footer, #MainMenu, .stDeployButton, div[data-testid="stToolbar"] {
        display: none !important;
    }
    .block-container {
        max-width: 1400px !important;
        padding: 24px 32px !important;
    }
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, sans-serif !important;
        background-color: #0b0d11 !important;
        color: #e6edf3 !important;
    }

    /* Top Command Header */
    .top-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-bottom: 20px;
        margin-bottom: 24px;
        border-bottom: 1px solid #1a1f29;
    }
    .brand-group {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .brand-icon {
        width: 10px;
        height: 10px;
        background: #3b82f6;
        border-radius: 2px;
    }
    .brand-title {
        font-size: 15px;
        font-weight: 600;
        letter-spacing: -0.01em;
        color: #f0f6fc;
    }
    .header-status {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 12px;
        color: #8b949e;
        font-family: 'JetBrains Mono', monospace;
    }
    .status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background-color: #22c55e;
    }

    /* Tab Switcher */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #12161f !important;
        border: 1px solid #1f2633 !important;
        border-radius: 8px !important;
        padding: 3px !important;
        gap: 4px !important;
        margin-bottom: 20px !important;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        color: #8b949e !important;
        padding: 6px 14px !important;
        background: transparent !important;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background: #1c2230 !important;
        color: #f0f6fc !important;
        font-weight: 600 !important;
    }

    /* KPI Cards */
    .metric-card {
        background-color: #12161f;
        border: 1px solid #1e2533;
        border-radius: 8px;
        padding: 16px 20px;
    }
    .metric-card-label {
        font-size: 12px;
        color: #8b949e;
        font-weight: 500;
        margin-bottom: 8px;
    }
    .metric-card-val {
        font-size: 28px;
        font-weight: 700;
        letter-spacing: -0.02em;
        line-height: 1;
    }
    .metric-pill {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 11px;
        font-weight: 500;
        font-family: 'JetBrains Mono', monospace;
        padding: 2px 6px;
        border-radius: 4px;
        margin-top: 8px;
    }
    .pill-green { background: rgba(34, 197, 94, 0.1); color: #4ade80; }
    .pill-red { background: rgba(239, 68, 68, 0.1); color: #f87171; }
    .pill-cyan { background: rgba(6, 182, 212, 0.1); color: #22d3ee; }

    /* Custom Table Wrapper */
    .saas-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
        background-color: #12161f;
        border: 1px solid #1e2533;
        border-radius: 8px;
        overflow: hidden;
    }
    .saas-table th {
        background-color: #0e1219;
        color: #64748b;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        padding: 10px 16px;
        text-align: left;
        border-bottom: 1px solid #1e2533;
    }
    .saas-table td {
        padding: 12px 16px;
        border-bottom: 1px solid #1a202c;
        color: #f0f6fc;
    }
    .saas-table tr:last-child td {
        border-bottom: none;
    }
    .mono-cell {
        font-family: 'JetBrains Mono', monospace;
    }

    /* Inputs & Buttons */
    div[data-testid="stTextInput"] input {
        background-color: #12161f !important;
        border: 1px solid #1e2533 !important;
        border-radius: 6px !important;
        color: #f0f6fc !important;
        font-size: 13px !important;
        font-family: 'JetBrains Mono', monospace !important;
        padding: 8px 12px !important;
    }
    div[data-testid="stButton"] button {
        background: #2563eb !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        padding: 8px 16px !important;
    }
    div[data-testid="stButton"] button:hover {
        background: #1d4ed8 !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Top Header Bar
# ---------------------------------------------------------------------------
st.markdown("""
<div class="top-header">
    <div class="brand-group">
        <div class="brand-icon"></div>
        <span class="brand-title">MarketSentry</span>
        <span style="font-size: 12px; color: #64748b; font-family: 'JetBrains Mono';">v0.5-quant</span>
    </div>
    <div class="header-status">
        <span class="status-dot"></span>
        <span>Local Node Online</span>
        <span style="color: #475569;">/</span>
        <span>Qwen 2.5 7B</span>
        <span style="color: #475569;">/</span>
        <span>ChromaDB Vector</span>
    </div>
</div>
""", unsafe_allow_html=True)

tab_overview, tab_scanner, tab_memory = st.tabs(["Overview & Audit", "Watchlist Scanner", "Vector Memory"])

WATCHLIST = ["NVDA", "TSLA", "AAPL", "MSFT", "GOOGL", "AMZN", "AMD"]

# ---------------------------------------------------------------------------
# TAB 1: OVERVIEW & FORENSIC AUDIT
# ---------------------------------------------------------------------------
with tab_overview:
    col_sym, col_btn, col_blank = st.columns([1.5, 1.2, 5.3])
    with col_sym:
        target_ticker = st.text_input("Equity Ticker", value="NVDA", label_visibility="collapsed").upper().strip()
    with col_btn:
        run_audit = st.button("Analyze Equity", use_container_width=True)

    if run_audit and target_ticker:
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        initial_state = {"ticker": target_ticker}

        status_box = st.status(f"Auditing {target_ticker}...", expanded=True)
        app = build_market_sentry_graph()
        final_state = {}

        for step_output in app.stream(initial_state, config=config):
            for node_name, node_state in step_output.items():
                if node_name == "init":
                    status_box.write("Initial state established. SQLite persistent checkpointer linked.")
                elif node_name == "bull_analyst":
                    status_box.write("Bull Agent: Multiples and growth metrics parsed.")
                    final_state["bull_thesis"] = node_state.get("bull_thesis")
                elif node_name == "bear_analyst":
                    status_box.write("Bear Agent: Form 10-K risk factors extracted.")
                    final_state["bear_thesis"] = node_state.get("bear_thesis")
                elif node_name == "audit_thesis":
                    audits = node_state.get("audit_history", [])
                    latest = audits[-1] if audits else None
                    round_num = node_state.get("audit_round", 1)
                    if latest and latest.passes_audit:
                        status_box.write(f"Skeptic Arbiter [Round {round_num}]: Grounding verified.")
                    else:
                        status_box.write(f"Skeptic Arbiter [Round {round_num}]: Claims challenged. Reflection loop active.")
                    final_state["audit_history"] = audits
                elif node_name == "synthesize_memo":
                    status_box.write("Synthesis: Historical vector precedents integrated.")
                    final_state["final_memo"] = node_state.get("final_memo")

        status_box.update(label=f"Analysis Complete: {target_ticker}", state="complete", expanded=False)

        memo = final_state.get("final_memo")
        if memo:
            # 1. Primary Metrics Row
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-card-label">Target Asset</div>
                    <div class="metric-card-val" style="color: #f0f6fc;">{memo.ticker}</div>
                    <span class="metric-pill pill-cyan">NASDAQ / US Equity</span>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                verdict_color = "#22c55e" if memo.verdict == "OVERWEIGHT" else ("#ef4444" if memo.verdict == "UNDERWEIGHT" else "#f59e0b")
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-card-label">Institutional Stance</div>
                    <div class="metric-card-val" style="color: {verdict_color};">{memo.verdict}</div>
                    <span class="metric-pill {'pill-green' if memo.verdict=='OVERWEIGHT' else 'pill-red'}">Final Trade Stance</span>
                </div>
                """, unsafe_allow_html=True)
            with c3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-card-label">Arbiter Conviction</div>
                    <div class="metric-card-val" style="color: #38bdf8;">{memo.conviction_score * 100:.1f}%</div>
                    <span class="metric-pill pill-cyan">Grounded Bayes Factor</span>
                </div>
                """, unsafe_allow_html=True)
            with c4:
                rounds = final_state.get("audit_round", 1)
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-card-label">Verification Rounds</div>
                    <div class="metric-card-val" style="color: #a855f7;">{rounds}</div>
                    <span class="metric-pill pill-cyan">Converged Reflection</span>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)

            # 2. Charts Row
            col_chart1, col_chart2 = st.columns([1.4, 1.0])
            with col_chart1:
                st.markdown("<p style='font-size: 12px; font-weight: 600; color: #8b949e; margin-bottom: 4px;'>PRICE ACTION & 2σ VOLATILITY ENVELOPE</p>", unsafe_allow_html=True)
                fig_market = generate_anomaly_chart(memo.ticker)
                st.plotly_chart(fig_market, use_container_width=True, config={'displayModeBar': False})

            with col_chart2:
                st.markdown("<p style='font-size: 12px; font-weight: 600; color: #8b949e; margin-bottom: 4px;'>DIALECTIC CONVICTION SPREAD</p>", unsafe_allow_html=True)
                bull = final_state.get("bull_thesis")
                bear = final_state.get("bear_thesis")
                if bull and bear:
                    fig_dialectic = generate_dialectic_comparison_chart(bull.key_points, bear.key_points)
                    st.plotly_chart(fig_dialectic, use_container_width=True, config={'displayModeBar': False})

            # 3. Executive Synthesis Panel
            st.markdown(f"""
            <div class="metric-card" style="margin-top: 16px;">
                <div class="metric-card-label">Executive Dialectic Synthesis</div>
                <div style="font-size: 14px; line-height: 1.6; color: #cbd5e1; margin-top: 8px;">
                    {memo.synthesis_memo}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # 4. Dialectic Evidence Matrices (HTML Tables)
        bull = final_state.get("bull_thesis")
        bear = final_state.get("bear_thesis")
        col_b, col_r = st.columns(2)

        with col_b:
            if bull:
                rows = "".join([f"<tr><td><strong>{p.point}</strong></td><td class='mono-cell' style='color:#94a3b8;'>{p.metric_or_citation}</td><td class='mono-cell' style='color:#4ade80; text-align:right;'>{p.confidence_score*100:.0f}%</td></tr>" for p in bull.key_points])
                st.markdown(f"""
                <div class="metric-card" style="margin-top: 16px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <span style="font-size:13px; font-weight:600; color:#4ade80;">Bullish Thesis</span>
                        <span class="metric-pill pill-green">Long Stance</span>
                    </div>
                    <div style="font-size:13px; color:#94a3b8; line-height:1.5; margin-bottom:12px;">{bull.summary}</div>
                    <table class="saas-table">
                        <thead>
                            <tr><th>Core Argument</th><th>Citation / Metric</th><th style="text-align:right;">Confidence</th></tr>
                        </thead>
                        <tbody>{rows}</tbody>
                    </table>
                </div>
                """, unsafe_allow_html=True)

        with col_r:
            if bear:
                rows = "".join([f"<tr><td><strong>{p.point}</strong></td><td class='mono-cell' style='color:#94a3b8;'>{p.metric_or_citation}</td><td class='mono-cell' style='color:#f87171; text-align:right;'>{p.confidence_score*100:.0f}%</td></tr>" for p in bear.key_points])
                st.markdown(f"""
                <div class="metric-card" style="margin-top: 16px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <span style="font-size:13px; font-weight:600; color:#f87171;">Bearish Thesis</span>
                        <span class="metric-pill pill-red">Short Stance</span>
                    </div>
                    <div style="font-size:13px; color:#94a3b8; line-height:1.5; margin-bottom:12px;">{bear.summary}</div>
                    <table class="saas-table">
                        <thead>
                            <tr><th>Risk Factor</th><th>SEC Citation</th><th style="text-align:right;">Confidence</th></tr>
                        </thead>
                        <tbody>{rows}</tbody>
                    </table>
                </div>
                """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# TAB 2: SENTINEL SCANNER
# ---------------------------------------------------------------------------
with tab_scanner:
    c_head, c_btn = st.columns([6, 1.5])
    with c_head:
        st.markdown("<p style='font-size: 13px; color: #8b949e; margin-top: 8px;'>Calculates intraday return Z-scores and 20-day average volume multiples across equities.</p>", unsafe_allow_html=True)
    with c_btn:
        start_scan = st.button("Scan Watchlist", use_container_width=True)

    if start_scan:
        sentinel = MarketSentinel(volume_threshold=1.5, z_score_threshold=1.8)
        results = []
        with st.spinner("Screening market distributions..."):
            for sym in WATCHLIST:
                res = sentinel.scan_ticker(sym)
                results.append(res)

        rows = ""
        for r in results:
            is_anom = r.get("is_anomaly")
            status_badge = '<span class="metric-pill pill-red">Anomaly</span>' if is_anom else '<span class="metric-pill pill-green">Normal</span>'
            ret_val = r.get('latest_return_pct', 0.0)
            ret_color = "#4ade80" if ret_val >= 0 else "#f87171"
            ret_sign = "+" if ret_val >= 0 else ""

            rows += f"""<tr>
                <td><strong>{r.get('ticker')}</strong></td>
                <td class="mono-cell">${r.get('latest_price', 0.0):.2f}</td>
                <td class="mono-cell" style="color:{ret_color};">{ret_sign}{ret_val}%</td>
                <td class="mono-cell" style="color:#94a3b8;">{r.get('z_score', 0.0)}σ</td>
                <td class="mono-cell" style="color:#94a3b8;">{r.get('volume_ratio', 1.0)}x</td>
                <td style="text-align:right;">{status_badge}</td>
            </tr>"""

        st.markdown(f"""
        <table class="saas-table" style="margin-top:16px;">
            <thead>
                <tr>
                    <th>Ticker</th>
                    <th>Price</th>
                    <th>Return</th>
                    <th>Z-Score</th>
                    <th>Volume Multiplier</th>
                    <th style="text-align:right;">Distribution Status</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# TAB 3: VECTOR MEMORY
# ---------------------------------------------------------------------------
with tab_memory:
    q_col, q_btn = st.columns([5, 1.5])
    with q_col:
        query_str = st.text_input("Semantic Query", value="capex expansion and data center infrastructure demand", label_visibility="collapsed")
    with q_btn:
        run_mem = st.button("Query Vector Vault", use_container_width=True)

    if run_mem:
        results = query_analogous_events(query_str, k=4)
        for r in results:
            st.markdown(f"""
            <div class="metric-card" style="margin-bottom: 12px; border-left: 3px solid #3b82f6;">
                <div style="font-size: 13.5px; font-weight: 500; color: #f0f6fc; margin-bottom: 6px;">{r['event_summary']}</div>
                <div style="font-family: 'JetBrains Mono'; font-size: 11px; color: #8b949e;">
                    Distance: <span style="color: #38bdf8;">{r['distance_score']}</span> &bull; 
                    Type: <span style="color: #a855f7;">{r['metadata'].get('event_type', 'ANALOGUE')}</span> &bull; 
                    Asset: <span style="color: #22c55e;">{r['metadata'].get('ticker', 'N/A')}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)