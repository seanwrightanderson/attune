from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_env: str = "development"
    secret_key: str = "dev-secret-change-in-prod"

    # API Keys
    anthropic_api_key: str
    openai_api_key: str

    # Database
    database_url: str = "sqlite+aiosqlite:///./attune.db"

    # Vector Store
    chroma_persist_dir: str = "./chroma_db"

    # CORS
    allowed_origins: str = "http://localhost:3000"

    # Tutor model
    claude_model: str = "claude-opus-4-6"
    embedding_model: str = "text-embedding-3-small"

    # RAG settings
    rag_top_k: int = 5
    max_history_turns: int = 10

    class Config:
        env_file = ".env"

    @property
    def origins_list(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
