"""
Global settings and configurations for MarketSentry.
"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM Settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:latest"
    EMBEDDING_MODEL: str = "nomic-embed-text"
    TEMPERATURE: float = 0.2

    # LangGraph System Parameters
    MAX_AUDIT_ROUNDS: int = 1
    CHECKPOINT_DB_PATH: str = "market_sentry_state.db"
    VECTOR_DB_DIR: str = os.path.join(os.getcwd(), "chroma_db")

    # SEC EDGAR Identity Header (Mandatory compliance format: Name AdminContact@domain.com)
    SEC_IDENTITY: str = "MarketSentryBot admin@marketsentry.internal"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()