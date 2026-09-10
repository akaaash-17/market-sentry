"""
Global settings and configurations for MarketSentry.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    # Selected based on your local Ollama installation
    OLLAMA_MODEL: str = "llama3.2:latest"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    # Model parameters optimized for CPU inference stability
    TEMPERATURE: float = 0.1
    
    # SEC EDGAR requires a declared User-Agent (Format: Name AdminContact@domain.com)
    SEC_IDENTITY: str = "MarketSentryAuditor student_researcher@localhost.local"
    
    # SQLite state database path for checkpoints
    CHECKPOINT_DB_PATH: str = "market_sentry_state.db"
    
    # Maximum revision/critique loops allowed in graph
    MAX_AUDIT_ROUNDS: int = 2

settings = Settings()