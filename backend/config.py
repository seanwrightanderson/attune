import os
from typing import List
from functools import lru_cache
from dotenv import load_dotenv

# Load .env file for local development (no-op if file doesn't exist)
load_dotenv()


class Settings:
    def __init__(self):
        self.app_env = os.environ.get("APP_ENV", "development")
        self.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-in-prod")

        # API Keys — required
        self.anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        self.openai_api_key = os.environ.get("OPENAI_API_KEY", "")

        # Database
        self.database_url = os.environ.get(
            "DATABASE_URL", "sqlite+aiosqlite:///./attune.db"
        )

        # Vector Store
        self.chroma_persist_dir = os.environ.get("CHROMA_PERSIST_DIR", "./chroma_db")

        # CORS
        self.allowed_origins = os.environ.get(
            "ALLOWED_ORIGINS", "http://localhost:3000"
        )

        # Models
        self.claude_model = os.environ.get("CLAUDE_MODEL", "claude-opus-4-6")
        self.embedding_model = os.environ.get(
            "EMBEDDING_MODEL", "text-embedding-3-small"
        )

        # RAG settings
        self.rag_top_k = int(os.environ.get("RAG_TOP_K", "5"))
        self.max_history_turns = int(os.environ.get("MAX_HISTORY_TURNS", "10"))

    @property
    def origins_list(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
