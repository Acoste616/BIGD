"""
Router dla endpointów zarządzania sesjami - uproszczona wersja
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.session_repository import SessionRepository
from app.repositories.client_repository import ClientRepository
from app.schemas.session import Session, SessionCreate, SessionCreateNested
import logging

logger = logging.getLogger(__name__)

# Inicjalizacja routera
router = APIRouter(
    tags=["sessions"],
    responses={
        404: {"description": "Sesja nie znaleziona"},
        400: {"description": "Nieprawidłowe dane wejściowe"}
    }
)

# Inicjalizacja repozytoriów
session_repo = SessionRepository()
client_repo = ClientRepository()


@router.post("/clients/{client_id}/sessions/", status_code=status.HTTP_201_CREATED)
async def create_session(
    client_id: int = Path(..., description="ID klienta"),
    session_data: Optional[SessionCreateNested] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Rozpocznij nową sesję dla klienta
    """
    try:
        # Sprawdź czy klient istnieje
        client = await client_repo.get_client(db, client_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Klient o ID {client_id} nie został znaleziony"
            )
        
        # Utwórz nową sesję
        new_session = await session_repo.create_session(db, client_id, session_data)
        
        logger.info(f"API: Utworzono sesję {new_session.id} dla klienta {client_id}")
        return new_session
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas tworzenia sesji: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas tworzenia sesji"
        )


@router.get("/clients/{client_id}/sessions/")
async def get_client_sessions(
    client_id: int = Path(..., description="ID klienta"),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="Liczba sesji do pominięcia"),
    limit: int = Query(100, ge=1, le=1000, description="Maksymalna liczba sesji")
):
    """
    Pobierz sesje klienta
    """
    try:
        # Sprawdź czy klient istnieje
        client = await client_repo.get_client(db, client_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Klient o ID {client_id} nie został znaleziony"
            )
        
        # Pobierz sesje klienta
        sessions = await session_repo.get_client_sessions(db, client_id, skip, limit)
        
        logger.info(f"API: Pobrano {len(sessions)} sesji dla klienta {client_id}")
        return sessions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas pobierania sesji: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas pobierania sesji"
        )


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: int = Path(..., description="ID sesji"),
    db: AsyncSession = Depends(get_db)
):
    """
    Pobierz szczegóły sesji
    """
    try:
        session = await session_repo.get_session(db, session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sesja o ID {session_id} nie została znaleziona"
            )
        
        logger.info(f"API: Pobrano sesję {session_id}")
        return session
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas pobierania sesji {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas pobierania szczegółów sesji"
        )