"""
Główny plik aplikacji FastAPI - Personal Sales AI Co-Pilot
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import (
    init_db, 
    close_db, 
    get_db,
    verify_database_connection,
    get_database_health
)

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Zarządzanie cyklem życia aplikacji.
    
    Inicjalizuje połączenia i zasoby przy starcie,
    oraz czyści je przy zamknięciu.
    """
    # Startup
    logger.info("="*60)
    logger.info(f"Uruchamianie {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Środowisko: {settings.ENVIRONMENT}")
    logger.info("="*60)
    
    try:
        # Inicjalizacja bazy danych
        await init_db()
        
        # Weryfikacja połączenia
        if await verify_database_connection():
            logger.info("✅ Połączenie z bazą danych aktywne")
        else:
            logger.warning("⚠️ Problem z połączeniem do bazy danych")
            
    except Exception as e:
        logger.error(f"❌ Błąd podczas uruchamiania aplikacji: {e}")
        raise
    
    logger.info("✅ Aplikacja uruchomiona pomyślnie")
    
    yield
    
    # Shutdown
    logger.info("Zamykanie aplikacji...")
    
    try:
        await close_db()
        logger.info("✅ Zasoby zwolnione pomyślnie")
    except Exception as e:
        logger.error(f"❌ Błąd podczas zamykania aplikacji: {e}")
        
    logger.info("Aplikacja zamknięta")


# Inicjalizacja aplikacji FastAPI
app = FastAPI(
    title="Personal Sales AI Co-Pilot",
    description="Inteligentny asystent sprzedaży wykorzystujący AI do analizy klientów i strategii sprzedażowych",
    version="0.1.0",
    lifespan=lifespan
)

# Konfiguracja CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """
    Endpoint główny - sprawdzenie działania API
    """
    return {
        "message": "Personal Sales AI Co-Pilot API",
        "version": "0.1.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Endpoint sprawdzający stan zdrowia aplikacji.
    
    Returns:
        Dict z informacjami o stanie aplikacji i połączeń
    """
    # Sprawdzenie stanu bazy danych
    db_health = await get_database_health()
    
    # Podstawowy status aplikacji
    app_health = {
        "status": "healthy" if db_health["status"] == "healthy" else "degraded",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG
    }
    
    # Szczegółowy status komponentów
    components = {
        "database": db_health,
        "qdrant": {
            "status": "not_implemented",
            "details": {"message": "Qdrant health check będzie dodany"}
        }
    }
    
    return {
        "application": app_health,
        "components": components,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health/db")
async def database_health_check(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    Szczegółowy health check bazy danych.
    
    Args:
        db: Sesja bazy danych (dependency injection)
        
    Returns:
        Dict z informacjami o stanie bazy danych
    """
    return await get_database_health()



# Import i rejestracja routerów
from app.routers import clients, sessions, interactions, feedback, knowledge

# Rejestracja routerów API
app.include_router(clients.router, prefix="/api/v1")
app.include_router(sessions.router, prefix="/api/v1")
app.include_router(interactions.router, prefix="/api/v1")
app.include_router(feedback.router, prefix="/api/v1")
app.include_router(knowledge.router, prefix="/api/v1")

# Przyszłe routery (do dodania w kolejnych krokach)
# from app.routers import auth, analysis
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
# app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
