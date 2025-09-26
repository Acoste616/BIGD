"""
Konfiguracja aplikacji - zarządzanie ustawieniami przez zmienne środowiskowe
"""
from typing import List

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

# Załadowanie zmiennych środowiskowych z pliku .env
load_dotenv()


class Settings(BaseSettings):
    """
    Główna klasa konfiguracji aplikacji
    """

    # Podstawowe ustawienia aplikacji
    APP_NAME: str = "Personal Sales AI Co-Pilot"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # Bezpieczeństwo
    SECRET_KEY: str = Field(
        default_factory=lambda: os.getenv(
            "SECRET_KEY", "your-secret-key-here-change-in-production"
        ),
        description="Secret key used to sign session cookies and CSRF tokens.",
    )
    JWT_SECRET_KEY: str = Field(
        default_factory=lambda: os.getenv("JWT_SECRET_KEY", "your-jwt-secret-key-here"),
        description="Secret used to sign JWT tokens.",
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # Baza danych PostgreSQL
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/sales_copilot"
    )

    # Qdrant Vector Database
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "sales_knowledge")

    # Ollama Cloud API (Turbo)
    OLLAMA_API_KEY: str = Field(
        default_factory=lambda: os.getenv("OLLAMA_API_KEY", ""),
        description="API key used to authenticate against the Ollama service.",
    )
    OLLAMA_API_URL: str = os.getenv("OLLAMA_API_URL", "https://ollama.com")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "gpt-oss:120b")
    OLLAMA_FALLBACK_MODEL: str = os.getenv("OLLAMA_FALLBACK_MODEL", "gpt-oss:20b")

    # CORS - Enhanced for development with multiple ports
    CORS_ORIGINS_STR: str = os.getenv(
        "CORS_ORIGINS_STR",
        "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:5173,http://localhost:8000",
    )

    @property
    def CORS_ORIGINS(self) -> List[str]:
        return self.CORS_ORIGINS_STR.split(",")

    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = int(os.getenv("WS_HEARTBEAT_INTERVAL", "30"))
    WS_CONNECTION_TIMEOUT: int = int(os.getenv("WS_CONNECTION_TIMEOUT", "60"))

    # Limity API
    MAX_TOKENS_PER_REQUEST: int = int(os.getenv("MAX_TOKENS_PER_REQUEST", "4000"))
    MAX_CONTEXT_LENGTH: int = int(os.getenv("MAX_CONTEXT_LENGTH", "8000"))
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_PERIOD: int = int(os.getenv("RATE_LIMIT_PERIOD", "3600"))

    class Config:
        env_file = ".env"
        case_sensitive = True

    @model_validator(mode="after")
    def _validate_security(self) -> "Settings":
        """Ensure sensitive values are configured when running outside of development."""

        if self.ENVIRONMENT.lower() in {"production", "staging"}:
            insecure_defaults = {
                "SECRET_KEY": "your-secret-key-here-change-in-production",
                "JWT_SECRET_KEY": "your-jwt-secret-key-here",
            }

            for field_name, default_value in insecure_defaults.items():
                value = getattr(self, field_name, "")
                if not value or value == default_value:
                    raise ValueError(
                        f"Configuration value {field_name} must be provided via environment variables in {self.ENVIRONMENT}.",
                    )

            if not self.OLLAMA_API_KEY:
                raise ValueError(
                    "OLLAMA_API_KEY must be configured when running in a non-development environment.",
                )

        return self


# Singleton instancja ustawień
settings = Settings()
