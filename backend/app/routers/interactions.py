"""
Router dla endpointów zarządzania interakcjami - uproszczona wersja
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.interaction_repository import InteractionRepository
from app.repositories.session_repository import SessionRepository
from app.schemas.interaction import Interaction, InteractionCreateNested
import logging

logger = logging.getLogger(__name__)

# Inicjalizacja routera
router = APIRouter(
    tags=["interactions"],
    responses={
        404: {"description": "Interakcja nie znaleziona"},
        400: {"description": "Nieprawidłowe dane wejściowe"}
    }
)

# Inicjalizacja repozytoriów
interaction_repo = InteractionRepository()
session_repo = SessionRepository()


@router.post("/sessions/{session_id}/interactions/", status_code=status.HTTP_201_CREATED)
async def create_interaction(
    interaction_data: InteractionCreateNested,
    session_id: int = Path(..., description="ID sesji"),
    db: AsyncSession = Depends(get_db)
):
    """
    Utwórz nową interakcję w sesji
    """
    try:
        # Sprawdź czy sesja istnieje - NAPRAWKA: get_session zamiast get
        session = await session_repo.get_session(db, session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sesja o ID {session_id} nie została znaleziona"
            )
        
        # Utwórz nową interakcję
        new_interaction = await interaction_repo.create_interaction(db, session_id, interaction_data)
        
        logger.info(f"API: Utworzono interakcję {new_interaction.id} w sesji {session_id}")
        return new_interaction
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas tworzenia interakcji: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas tworzenia interakcji"
        )


@router.get("/sessions/{session_id}/interactions/")
async def get_session_interactions(
    session_id: int = Path(..., description="ID sesji"),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="Liczba interakcji do pominięcia"),
    limit: int = Query(100, ge=1, le=1000, description="Maksymalna liczba interakcji")
):
    """
    Pobierz interakcje dla sesji
    """
    try:
        # Sprawdź czy sesja istnieje - NAPRAWKA: get_session zamiast get
        session = await session_repo.get_session(db, session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sesja o ID {session_id} nie została znaleziona"
            )
        
        # Pobierz interakcje sesji
        interactions = await interaction_repo.get_session_interactions(db, session_id, skip, limit)
        
        logger.info(f"API: Pobrano {len(interactions)} interakcji dla sesji {session_id}")
        return interactions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas pobierania interakcji: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas pobierania interakcji"
        )


@router.get("/interactions/{interaction_id}")
async def get_interaction(
    interaction_id: int = Path(..., description="ID interakcji"),
    db: AsyncSession = Depends(get_db)
):
    """
    Pobierz szczegóły interakcji
    """
    try:
        interaction = await interaction_repo.get_interaction(db, interaction_id)
        
        if not interaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Interakcja o ID {interaction_id} nie została znaleziona"
            )
        
        logger.info(f"API: Pobrano interakcję {interaction_id}")
        return interaction
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas pobierania interakcji {interaction_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas pobierania szczegółów interakcji"
        )