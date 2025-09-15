"""
Router dla endpointów zarządzania sesjami - uproszczona wersja
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.session_repository import SessionRepository
from app.repositories.client_repository import ClientRepository
from app.schemas.session import Session, SessionCreate, SessionCreateNested, SessionConclusion
from app.schemas.indicators import SalesIndicatorsAnalysis
from app.services.sales_indicators_service import SalesIndicatorsService
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

# Inicjalizacja serwisów
sales_indicators_service = SalesIndicatorsService()


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


# Add the new GET /sessions endpoint
@router.get("/sessions/")
async def get_all_sessions(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="Liczba sesji do pominięcia"),
    limit: int = Query(100, ge=1, le=1000, description="Maksymalna liczba sesji")
):
    """
    Pobierz wszystkie sesje dla dashboardu
    """
    try:
        sessions = await session_repo.get_sessions(db, skip, limit)
        logger.info(f"API: Pobrano {len(sessions)} sesji")
        return sessions
    except Exception as e:
        logger.error(f"Błąd podczas pobierania sesji: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas pobierania sesji"
        )


# Add the new POST /sessions/{session_id}/conclude endpoint
@router.post("/sessions/{session_id}/conclude")
async def conclude_session(
    session_id: int = Path(..., description="ID sesji"),
    db: AsyncSession = Depends(get_db),
    conclusion_data: SessionConclusion = None
):
    """
    Finalizuje sesję, ustawiając jej status na 'closed' i zapisując dane wyniku
    """
    try:
        # Pobierz sesję
        session = await session_repo.get_session(db, session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sesja o ID {session_id} nie została znaleziona"
            )
        
        # Sprawdź czy sesja nie jest już zamknięta
        if session.status == 'closed':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Sesja o ID {session_id} jest już zamknięta"
            )
        
        # Przygotuj dane outcome
        outcome_data = {
            "outcome": conclusion_data.outcome,
            "notes": conclusion_data.notes,
            "summary": conclusion_data.summary
        }
        
        # Aktualizuj sesję
        updated_session = await session_repo.update_session(
            db, 
            session_id, 
            {
                "status": "closed",
                "outcome_data": outcome_data
            }
        )
        
        if not updated_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sesja o ID {session_id} nie została znaleziona"
            )
        
        logger.info(f"API: Zakończono sesję {session_id}")
        return updated_session
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas kończenia sesji {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas kończenia sesji"
        )


@router.get("/sessions/{session_id}/psychometrics")
async def get_session_psychometrics(
    session_id: int = Path(..., description="ID sesji"),
    db: AsyncSession = Depends(get_db)
):
    """
    Pobierz agregowane dane psychometryczne dla konkretnej sesji
    
    Args:
        session_id: ID sesji
        
    Returns:
        PsychometricData: Dane psychometryczne sesji
        
    Raises:
        HTTPException: Gdy sesja nie została znaleziona (404)
    """
    try:
        # Pobierz sesję z danymi psychometrycznymi
        session = await session_repo.get_session(db, session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sesja o ID {session_id} nie została znaleziona"
            )
        
        # Przygotuj dane do zwrócenia
        psychometric_data = {
            "confidence_score": session.psychology_confidence or 0,
            "summary": "Profil psychometryczny klienta na podstawie analizy sesji",
            "big_five": session.cumulative_psychology.get("big_five", {}) if session.cumulative_psychology else {},
            "archetype": session.customer_archetype or {},
            "disc_profile": session.cumulative_psychology.get("disc", {}) if session.cumulative_psychology else {},
            "schwartz_values": session.cumulative_psychology.get("schwartz_values", []) if session.cumulative_psychology else [],
            "evolution_trend": {
                "big_five_trends": {},
                "disc_trends": {},
                "schwartz_trends": {}
            }
        }
        
        return psychometric_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas pobierania danych psychometrycznych dla sesji {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas pobierania danych psychometrycznych"
        )


@router.get("/sessions/{session_id}/indicators", response_model=SalesIndicatorsAnalysis)
async def get_session_indicators(
    session_id: int = Path(..., description="ID sesji"),
    db: AsyncSession = Depends(get_db)
):
    """
    Pobierz wskaźniki sprzedażowe dla konkretnej sesji
    
    Args:
        session_id: ID sesji
        
    Returns:
        SalesIndicatorsAnalysis: Kompletna analiza wskaźników sprzedażowych
        
    Raises:
        HTTPException: Gdy sesja nie została znaleziona (404)
    """
    try:
        # Pobierz sesję z danymi psychometrycznymi
        session = await session_repo.get_session(db, session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sesja o ID {session_id} nie została znaleziona"
            )
        
        # Przygotuj dane psychometryczne do obliczeń
        psychometric_data = {
            "confidence_score": session.psychology_confidence or 0,
            "big_five": session.cumulative_psychology.get("big_five", {}) if session.cumulative_psychology else {},
            "disc": session.cumulative_psychology.get("disc", {}) if session.cumulative_psychology else {},
            "schwartz_values": session.cumulative_psychology.get("schwartz_values", []) if session.cumulative_psychology else [],
            "archetype": session.customer_archetype or {}
        }
        
        # Oblicz wskaźniki sprzedażowe
        indicators = sales_indicators_service.calculate_indicators(psychometric_data)
        
        # Dodaj metadane
        indicators.session_id = session_id
        
        return indicators
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas pobierania wskaźników sprzedażowych dla sesji {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas obliczania wskaźników sprzedażowych"
        )
