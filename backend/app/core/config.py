"""
Konfiguracja aplikacji - zarządzanie ustawieniami przez zmienne środowiskowe
"""
from pydantic_settings import BaseSettings
from typing import List
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
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-jwt-secret-key-here")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # Baza danych PostgreSQL
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@localhost:5432/sales_copilot"
    )
    
    # Qdrant Vector Database
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "sales_knowledge")
    
    # Ollama Cloud API (Turbo)
    OLLAMA_API_KEY: str = os.getenv("OLLAMA_API_KEY", "")
    OLLAMA_API_URL: str = os.getenv("OLLAMA_API_URL", "https://ollama.com")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "gpt-oss:120b")
    OLLAMA_FALLBACK_MODEL: str = os.getenv("OLLAMA_FALLBACK_MODEL", "gpt-oss:20b")
    
    # CORS - Enhanced for development with multiple ports
    CORS_ORIGINS_STR: str = os.getenv(
        "CORS_ORIGINS_STR", 
        "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:5173,http://localhost:8000"
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


# Singleton instancja ustawień
settings = Settings()
