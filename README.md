# MarketSentry 🛡️
### Autonomous Adversarial Market Intelligence Graph

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python&logoColor=white)](#)
[![LangGraph](https://img.shields.io/badge/Orchestrator-LangGraph-FF6F00.svg)](#)
[![Ollama](https://img.shields.io/badge/Local_Inference-Ollama-black.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Cost](https://img.shields.io/badge/Inference_Cost-$0.00-brightgreen.svg)](#)

MarketSentry is an institutional-grade, zero-cost market intelligence engine built with **LangGraph** and local open-weights LLMs via **Ollama**. 

Unlike standard linear summarization chains or echo-chamber LLM prompts, MarketSentry deploys a **dialectic multi-agent architecture** (Thesis $\rightarrow$ Antithesis $\rightarrow$ Synthesis) with a **hybrid deterministic reflection loop** that programmatically challenges claims against raw SEC EDGAR 10-K filings and real-time market data.

---

## 📊 Empirical System Benchmark

MarketSentry includes an automated evaluation harness (`eval/benchmark.py`) to quantify evidence grounding, hallucination rates, and convergence latency on consumer hardware (Intel i5 CPU via Ollama):

| Ticker | Latency (s) | Reflection Rounds | Total Claims | Grounding Rate | Deterministic Error Rate | CIO Verdict | Conviction |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **AAPL** | 437.64s | 1 | 13 | **100.0%** | **0.0%** | NEUTRAL | 50.0% |
| **NVDA** | 236.88s | 2 | 13 | **100.0%** | **0.0%** | NEUTRAL | 50.0% |
| **MSFT** | 268.56s | 2 | 14 | **100.0%** | **0.0%** | OVERWEIGHT | 80.0% |
| **TSLA** | 281.48s | 2 | 12 | **100.0%** | **0.0%** | NEUTRAL | 50.0% |
| **AGGREGATE** | **306.14s** | **1.75** | **52** | **100.0%** | **0.0%** | — | — |

* **Zero Hallucinations:** 100% of claims deterministically matched against ground-truth JSON data.
* **Autonomous Convergence:** The reflection loop converges in an average of 1.75 rounds.

---

## 🏛️ System Architecture

```text
                         [Watchlist Stream]
                                 │
                                 ▼
                     ┌──────────────────────┐
                     │   Sentinel Engine    │
                     │ (Z-Score/Vol Anomaly)│
                     └──────────┬───────────┘
                                │ (Anomaly Alert)
                                ▼
                     ┌──────────────────────┐
                     │    Init & Router     │
                     └──────────┬───────────┘
                                │
                ┌───────────────┴───────────────┐
                ▼                               ▼
     ┌─────────────────────┐         ┌─────────────────────┐
     │     Bull Analyst    │         │     Bear Analyst    │
     │  (Tool-Calling)     │         │  (SEC Item 1A Tool) │
     └──────────┬──────────┘         └──────────┬──────────┘
                │                               │
                └───────────────┬───────────────┘
                                ▼
                   ┌─────────────────────────┐
                   │     Skeptic Arbiter     │ ◄───┐
                   │  (Deterministic Math +  │     │ (Reflection
                   │      LLM Audit)         │     │  Loop if claims
                   └────────────┬────────────┘     │  are ungrounded)
                                │                  │
                   [Audit Passed or Max Rounds?]───┘
                                │ (Yes)
                                ▼
                   ┌─────────────────────────┐
                   │  CIO Synthesis Memo     │
                   │  (Trade Allocation)     │
                   └────────────┬────────────┘
                                ▼
                              [END]
Key Engineering Highlights
Autonomous Sentinel Monitoring: Event-driven daemon calculates intraday return z-scores and volume surges, triggering forensic graph execution without human input.

Dynamic ReAct Tool Calling: Agents autonomously select and invoke granular financial tools (get_valuation_multiples, get_financial_health, get_market_consensus, fetch_sec_risk_disclosures).

Hybrid Deterministic Auditing: Python math validation layer parses extracted figures and flags discrepancies before LLM evaluation.

Persistent Checkpointing: Uses SqliteSaver to store thread execution history directly in local SQLite databases for audit replay and state continuity.

100% Zero-Cost Edge Inference: Runs locally on consumer CPUs using open-weights models via Ollama.

🚀 Quickstart
Prerequisites
Install Ollama and pull a model:

Bash
ollama run qwen2.5:7b-instruct
Python 3.11+

Installation
Bash
git clone [https://github.com/akaaash-17/market-sentry.git](https://github.com/akaaash-17/market-sentry.git)
cd market-sentry

python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
Running MarketSentry
1. Interactive Streamlit Dashboard (Deep Dive & Sentinel Scanner):

Bash
streamlit run app.py
2. CLI Deep Dive Runner:

Bash
python main.py
3. Autonomous Background Sentinel Daemon:

Bash
python sentinel_daemon.py
4. Run Empirical Benchmarks:

Bash
python eval/benchmark.py
📂 Project Structure
Plaintext
market-sentry/
├── app.py                      # Interactive Streamlit Web UI (Audit & Scanner)
├── main.py                     # CLI Rich Terminal Interface
├── sentinel_daemon.py          # Continuous Background Watchlist Monitor
├── requirements.txt            # Project dependencies
├── config/
│   └── settings.py             # Global configurations & SEC user-agent
├── eval/
│   └── benchmark.py            # Quantitative evaluation framework
├── src/
│   ├── state.py                # TypedDict state, Pydantic V2 schemas & validators
│   ├── graph.py                # LangGraph StateGraph, cyclic edges & SQLite checkpointer
│   ├── tools/
│   │   ├── market_feed.py      # Granular valuation and financial health tools
│   │   ├── sec_edgar.py        # SEC Form 10-K Item 1A parser
│   │   └── anomaly_detector.py # Z-score volatility & volume surge detector
│   └── agents/
│       ├── bull_analyst.py     # Growth upside specialist with tool-calling
│       ├── bear_analyst.py     # Forensic short & risk analyst
│       └── skeptic_arbiter.py  # Hybrid deterministic verifier & CIO synthesizer
📄 License
This project is open-source under the MIT License.


---

### Step 2: Commit and Tag Milestone v0.4

Run these commands in your VS Code terminal to commit the evaluation suite, updated README, and push the tag to GitHub:

```powershell
git add .
git commit -m "feat(v0.4): add automated benchmark harness and update README with empirical results"
git tag -a v0.4-benchmark-eval -m "v0.4: Automated evaluation framework measuring grounding accuracy, unsupported claim rates, and CPU latency"
git push origin main --tags