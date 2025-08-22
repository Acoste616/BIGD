"""
Konfiguracja połączenia z bazą danych PostgreSQL
Asynchroniczne połączenie z wykorzystaniem asyncpg i SQLAlchemy 2.0
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import (
    create_async_engine, 
    AsyncSession, 
    async_sessionmaker,
    AsyncEngine
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool, QueuePool
from sqlalchemy import text, select
from app.core.config import settings
import logging
import asyncio

logger = logging.getLogger(__name__)

# Konwersja URL dla async z asyncpg
def get_database_url() -> str:
    """
    Konwertuje URL bazy danych do formatu async
    """
    url = settings.DATABASE_URL
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://")
    return url

DATABASE_URL = get_database_url()

# Konfiguracja parametrów połączenia
engine_args = {
    "echo": settings.DEBUG,  # Logowanie zapytań SQL w trybie debug
    "echo_pool": settings.DEBUG and False,  # Logowanie pool events (opcjonalne)
    "pool_pre_ping": True,  # Sprawdzanie połączenia przed użyciem
    "pool_recycle": 3600,  # Recyklowanie połączeń co godzinę
    "connect_args": {
        "server_settings": {
            "application_name": settings.APP_NAME,
            "jit": "off"
        },
        "command_timeout": 60,
        "timeout": 10,
    }
}

# Wybór typu pool'a w zależności od środowiska
if settings.ENVIRONMENT == "test":
    # Dla testów używamy NullPool (bez poolingu)
    engine_args["poolclass"] = NullPool
else:
    # Dla produkcji używamy domyślny async pool z optymalnymi parametrami
    engine_args.update({
        "pool_size": 20,  # Liczba stałych połączeń
        "max_overflow": 40,  # Maksymalna liczba dodatkowych połączeń
        # poolclass automatycznie wybrane dla async engine
    })

# Utworzenie silnika bazy danych
engine: AsyncEngine = create_async_engine(DATABASE_URL, **engine_args)

# Fabryka sesji - konfiguracja dla async
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Nie wygaszaj obiektów po commit
    autocommit=False,  # Wymagaj jawnego commit
    autoflush=False,  # Nie flushuj automatycznie przed zapytaniami
)

# Bazowa klasa dla modeli - używamy nowoczesnego podejścia
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    Bazowa klasa dla wszystkich modeli SQLAlchemy
    """
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency injection dla sesji bazy danych.
    
    Tworzy nową sesję dla każdego żądania HTTP i gwarantuje
    jej poprawne zamknięcie po zakończeniu obsługi żądania.
    
    Yields:
        AsyncSession: Asynchroniczna sesja bazy danych
        
    Example:
        ```python
        @router.get("/clients")
        async def get_clients(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Client))
            return result.scalars().all()
        ```
    """
    async with AsyncSessionLocal() as session:
        try:
            # Rozpocznij transakcję
            async with session.begin():
                yield session
            # Commit zostanie wykonany automatycznie jeśli nie było błędu
        except Exception as e:
            # Rollback zostanie wykonany automatycznie przy błędzie
            logger.error(f"Błąd podczas transakcji bazy danych: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Inicjalizacja bazy danych - tworzenie tabel.
    
    Importuje wszystkie modele i tworzy tabele jeśli nie istnieją.
    Wywołanie przy starcie aplikacji.
    """
    try:
        # Import wszystkich modeli, aby były zarejestrowane w Base.metadata
        from app.models import Client, Session, Interaction
        
        logger.info("Inicjalizacja bazy danych...")
        
        async with engine.begin() as conn:
            # Utworzenie wszystkich tabel jeśli nie istnieją
            await conn.run_sync(Base.metadata.create_all)
            
        logger.info("Baza danych zainicjalizowana pomyślnie")
        logger.info(f"Zarejestrowane tabele: {', '.join(Base.metadata.tables.keys())}")
        
        # Weryfikacja połączenia
        await verify_database_connection()
        
    except Exception as e:
        logger.error(f"Błąd podczas inicjalizacji bazy danych: {e}")
        raise


async def close_db() -> None:
    """
    Zamknięcie połączenia z bazą danych.
    
    Wywołanie przy zamykaniu aplikacji.
    """
    try:
        await engine.dispose()
        logger.info("Połączenie z bazą danych zamknięte")
    except Exception as e:
        logger.error(f"Błąd podczas zamykania połączenia z bazą: {e}")
        raise


async def verify_database_connection() -> bool:
    """
    Weryfikacja połączenia z bazą danych.
    
    Returns:
        bool: True jeśli połączenie działa, False w przeciwnym razie
    """
    try:
        async with AsyncSessionLocal() as session:
            # Proste zapytanie testowe
            result = await session.execute(text("SELECT 1"))
            result.scalar()
            logger.info("Połączenie z bazą danych zweryfikowane pomyślnie")
            return True
    except Exception as e:
        logger.error(f"Błąd weryfikacji połączenia z bazą: {e}")
        return False


async def get_database_health() -> dict:
    """
    Sprawdzenie stanu zdrowia bazy danych.
    
    Returns:
        dict: Informacje o stanie bazy danych
    """
    health = {
        "status": "unhealthy",
        "database": "disconnected",
        "details": {}
    }
    
    try:
        async with AsyncSessionLocal() as session:
            # Test połączenia
            result = await session.execute(text("SELECT version()"))
            version = result.scalar()
            
            # Sprawdzenie liczby tabel
            result = await session.execute(
                text("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
            )
            table_count = result.scalar()
            
            # Informacje o pool'u połączeń
            pool = engine.pool
            pool_status = {
                "size": pool.size() if hasattr(pool, 'size') else 'N/A',
                "checked_in": pool.checkedin() if hasattr(pool, 'checkedin') else 'N/A',
                "overflow": pool.overflow() if hasattr(pool, 'overflow') else 'N/A',
                "total": pool.total() if hasattr(pool, 'total') else 'N/A',
            }
            
            health.update({
                "status": "healthy",
                "database": "connected",
                "details": {
                    "version": version,
                    "tables_count": table_count,
                    "pool_status": pool_status,
                    "url": DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'hidden'
                }
            })
            
    except Exception as e:
        health["details"]["error"] = str(e)
        logger.error(f"Database health check failed: {e}")
    
    return health


@asynccontextmanager
async def get_db_transaction():
    """
    Context manager dla transakcji bazodanowych.
    
    Użycie:
        async with get_db_transaction() as db:
            # wykonaj operacje
            await db.commit()  # opcjonalne, commit automatyczny przy wyjściu
    
    Yields:
        AsyncSession: Sesja z aktywną transakcją
    """
    async with AsyncSessionLocal() as session:
        async with session.begin():
            try:
                yield session
            except Exception:
                await session.rollback()
                raise


async def execute_raw_query(query: str, params: dict = None) -> list:
    """
    Wykonanie surowego zapytania SQL.
    
    Args:
        query: Zapytanie SQL
        params: Parametry zapytania
        
    Returns:
        list: Wyniki zapytania
        
    Warning:
        Używaj tylko dla zaawansowanych operacji, preferuj ORM
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(text(query), params or {})
        return result.fetchall()


# Alias dla kompatybilności wstecznej
get_session = get_db
