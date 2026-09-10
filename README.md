# MarketSentry 🛡️
### Autonomous Adversarial Market Intelligence Graph

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python&logoColor=white)](#)
[![LangGraph](https://img.shields.io/badge/Orchestrator-LangGraph-FF6F00.svg)](#)
[![Ollama](https://img.shields.io/badge/Local_Inference-Ollama-black.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Cost](https://img.shields.io/badge/Inference_Cost-$0.00-brightgreen.svg)](#)

MarketSentry is an institutional-grade, zero-cost market analysis agent built with **LangGraph** and local open-weights LLMs via **Ollama**. 

Unlike standard linear summarization chains or echo-chamber LLM prompts, MarketSentry deploys a **dialectic multi-agent architecture** (Thesis $\rightarrow$ Antithesis $\rightarrow$ Synthesis) with a **cyclic Skeptic reflection loop** that programmatically challenges claims against raw SEC EDGAR 10-K filings and real-time market data.

---

## 🏛️ System Architecture

```text
                       ┌──────────────────────┐
                       │   Data Ingestion     │
                       │ (yfinance + SEC 10-K)│
                       └──────────┬───────────┘
                                  │
                  ┌───────────────┴───────────────┐
                  ▼                               ▼
       ┌─────────────────────┐         ┌─────────────────────┐
       │     Bull Analyst    │         │     Bear Analyst    │
       │ (Valuation/Growth)  │         │ (Downside/SEC 1A)   │
       └──────────┬──────────┘         └──────────┬──────────┘
                  │                               │
                  └───────────────┬───────────────┘
                                  ▼
                     ┌─────────────────────────┐
                     │     Skeptic Arbiter     │ ◄───┐
                     │   (Fact-Checking Audit) │     │ (Reflection
                     └────────────┬────────────┘     │  Loop if claims
                                  │                  │  are ungrounded)
                     [Audit Passed or Max Rounds?]───┘
                                  │ (Yes)
                                  ▼
                     ┌─────────────────────────┐
                     │  CIO Synthesis Memo     │
                     │  (Trade Allocation)     │
                     └────────────┬────────────┘
                                  ▼
                                [END]
Key Engineering Distinctions
Stateful Cyclical Execution: Uses LangGraph's StateGraph with conditional edges to automatically reject hallucinated numbers and route agents back for evidence re-grounding.

100% Zero-Cost & Private: Runs entirely on local CPU/GPU hardware using Ollama (qwen2.5:7b / llama3.1:8b). Requires zero paid API subscriptions (no OpenAI, no Tavily, no SerpAPI).

Strict Pydantic V2 Schemas: Every agent returns strictly validated schemas with custom pre-validators that normalize model outputs.

Audit Persistence: Integrates LangGraph checkpointers (MemorySaver) for thread-isolated state inspection and session continuity.

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
CLI Institutional Terminal:

Bash
python main.py
Interactive Streamlit Dashboard:

Bash
streamlit run app.py
📂 Project Structure
Plaintext
market-sentry/
├── app.py                      # Interactive Streamlit Web UI
├── main.py                     # CLI Rich Terminal Interface
├── requirements.txt            # Minimal dependencies
├── config/
│   └── settings.py             # System configuration & SEC identity
├── src/
│   ├── state.py                # TypedDict state & Pydantic V2 schemas
│   ├── graph.py                # LangGraph StateGraph, conditional edges & checkpointer
│   ├── tools/
│   │   ├── market_feed.py      # Real-time yfinance market multiples
│   │   └── sec_edgar.py        # Institutional Form 10-K Item 1A parser
│   └── agents/
│       ├── bull_analyst.py     # Growth upside specialist
│       ├── bear_analyst.py     # Forensic risk and short-thesis specialist
│       └── skeptic_arbiter.py  # Fact-checker & Chief Investment Officer synthesizer
📄 License
This project is open-source under the MIT License.