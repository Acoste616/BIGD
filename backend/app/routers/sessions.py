"""
Router dla endpointów zarządzania sesjami rozmów
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.db_utils import PaginationParams
from app.repositories.session_repository import SessionRepository
from app.repositories.client_repository import ClientRepository
from app.schemas.session import (
    Session,
    SessionCreate,
    SessionCreateNested,
    SessionCreateDemo,
    SessionDemo,
    SessionUpdate,
    SessionEnd,
    SessionWithClient,
    SessionWithInteractions,
    SessionSummary,
    SessionAnalytics
)
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


# === ENDPOINTY ZAGNIEŻDŻONE POD KLIENTEM ===

@router.post("/clients/{client_id}/sessions/", response_model=Session, status_code=status.HTTP_201_CREATED)
async def create_session(
    client_id: int = Path(..., description="ID klienta"),
    session_data: Optional[SessionCreateNested] = None,
    db: AsyncSession = Depends(get_db)
) -> Session:
    """
    Rozpocznij nową sesję dla klienta
    
    Automatycznie kończy poprzednią aktywną sesję jeśli istnieje.
    
    Args:
        client_id: ID klienta
        session_data: Opcjonalne dane początkowe sesji
        db: Sesja bazy danych
        
    Returns:
        Utworzona sesja
        
    Raises:
        HTTPException: Gdy klient nie istnieje
    """
    try:
        # Sprawdź czy klient istnieje
        client = await client_repo.get(db, client_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Klient o ID {client_id} nie został znaleziony"
            )
        
        # Utwórz nową sesję
        new_session = await session_repo.create_session(
            db=db,
            client_id=client_id,
            session_data=session_data
        )
        
        logger.info(f"API: Utworzono sesję {new_session.id} dla klienta {client_id}")
        return Session.model_validate(new_session)
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Błąd podczas tworzenia sesji: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas tworzenia sesji"
        )


@router.get("/clients/{client_id}/sessions/", response_model=Dict[str, Any])
async def get_client_sessions(
    client_id: int = Path(..., description="ID klienta"),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Numer strony"),
    page_size: int = Query(20, ge=1, le=100, description="Liczba wyników na stronę"),
    only_active: bool = Query(False, description="Tylko aktywne sesje"),
    session_type: Optional[str] = Query(None, description="Typ sesji"),
    order_by: Optional[str] = Query(None, description="Pole do sortowania"),
    order_desc: bool = Query(True, description="Sortowanie malejące")
) -> Dict[str, Any]:
    """
    Pobierz listę sesji klienta z paginacją
    
    Args:
        client_id: ID klienta
        db: Sesja bazy danych
        page: Numer strony
        page_size: Rozmiar strony
        only_active: Czy tylko aktywne sesje
        session_type: Filtr typu sesji
        order_by: Pole sortowania
        order_desc: Czy sortować malejąco
        
    Returns:
        Lista sesji z metadanymi paginacji
        
    Raises:
        HTTPException: Gdy klient nie istnieje
    """
    try:
        # Sprawdź czy klient istnieje
        client = await client_repo.get(db, client_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Klient o ID {client_id} nie został znaleziony"
            )
        
        # Przygotuj parametry paginacji
        pagination = PaginationParams(
            page=page,
            page_size=page_size,
            order_by=order_by,
            order_desc=order_desc
        )
        
        # Pobierz sesje
        result = await session_repo.get_client_sessions(
            db=db,
            client_id=client_id,
            pagination=pagination,
            only_active=only_active,
            session_type=session_type
        )
        
        # Konwertuj do odpowiedzi
        response = result.dict()
        
        # Konwertuj obiekty Session do schematów Pydantic
        response["items"] = [
            Session.model_validate(session) 
            for session in result.items
        ]
        
        # Dodaj informacje o kliencie
        response["client"] = {
            "id": client.id,
            "name": client.name,
            "company": client.company
        }
        
        logger.info(f"API: Pobrano {len(result.items)} sesji dla klienta {client_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas pobierania sesji klienta {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas pobierania listy sesji"
        )


# === ENDPOINTY BEZPOŚREDNIE DLA SESJI ===

@router.get("/sessions/{session_id}", response_model=Session)
async def get_session(
    session_id: int = Path(..., description="ID sesji"),
    include_client: bool = Query(False, description="Czy dołączyć dane klienta"),
    include_interactions: bool = Query(False, description="Czy dołączyć interakcje"),
    db: AsyncSession = Depends(get_db)
) -> Session:
    """
    Pobierz szczegóły sesji po ID
    
    Args:
        session_id: ID sesji
        include_client: Czy dołączyć dane klienta
        include_interactions: Czy dołączyć listę interakcji
        db: Sesja bazy danych
        
    Returns:
        Dane sesji
        
    Raises:
        HTTPException: Gdy sesja nie istnieje
    """
    try:
        session = await session_repo.get_session(
            db=db,
            session_id=session_id,
            include_client=include_client,
            include_interactions=include_interactions
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sesja o ID {session_id} nie została znaleziona"
            )
        
        logger.info(f"API: Pobrano dane sesji ID: {session_id}")
        
        # Wybierz odpowiedni schemat w zależności od opcji
        if include_interactions:
            return SessionWithInteractions.model_validate(session)
        elif include_client:
            return SessionWithClient.model_validate(session)
        else:
            return Session.model_validate(session)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas pobierania sesji {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas pobierania danych sesji"
        )


@router.put("/sessions/{session_id}", response_model=Session)
async def update_session(
    session_id: int = Path(..., description="ID sesji"),
    update_data: SessionUpdate = ...,
    db: AsyncSession = Depends(get_db)
) -> Session:
    """
    Zaktualizuj dane sesji
    
    Args:
        session_id: ID sesji do aktualizacji
        update_data: Nowe dane sesji
        db: Sesja bazy danych
        
    Returns:
        Zaktualizowana sesja
        
    Raises:
        HTTPException: Gdy sesja nie istnieje
    """
    try:
        # Aktualizuj sesję
        updated_session = await session_repo.update_session(
            db=db,
            session_id=session_id,
            update_data=update_data
        )
        
        if not updated_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sesja o ID {session_id} nie została znaleziona"
            )
        
        logger.info(f"API: Zaktualizowano sesję ID: {session_id}")
        return Session.model_validate(updated_session)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas aktualizacji sesji {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas aktualizacji sesji"
        )


@router.put("/sessions/{session_id}/end", response_model=Session)
async def end_session(
    session_id: int = Path(..., description="ID sesji"),
    end_data: SessionEnd = ...,
    db: AsyncSession = Depends(get_db)
) -> Session:
    """
    Zakończ sesję
    
    Specjalny endpoint do zakończenia sesji z podsumowaniem.
    
    Args:
        session_id: ID sesji do zakończenia
        end_data: Dane końcowe (podsumowanie, wynik, oceny)
        db: Sesja bazy danych
        
    Returns:
        Zakończona sesja
        
    Raises:
        HTTPException: Gdy sesja nie istnieje lub jest już zakończona
    """
    try:
        # Zakończ sesję
        ended_session = await session_repo.end_session(
            db=db,
            session_id=session_id,
            end_data=end_data
        )
        
        if not ended_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sesja o ID {session_id} nie została znaleziona"
            )
        
        logger.info(f"API: Zakończono sesję ID: {session_id}")
        return Session.model_validate(ended_session)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas kończenia sesji {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas kończenia sesji"
        )


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: int = Path(..., description="ID sesji"),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Usuń sesję (wraz z wszystkimi interakcjami - kaskadowo)
    
    Args:
        session_id: ID sesji do usunięcia
        db: Sesja bazy danych
        
    Raises:
        HTTPException: Gdy sesja nie istnieje
    """
    try:
        success = await session_repo.delete_session(db, session_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sesja o ID {session_id} nie została znaleziona"
            )
        
        logger.info(f"API: Usunięto sesję ID: {session_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas usuwania sesji {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas usuwania sesji"
        )


# === DODATKOWE ENDPOINTY ===

@router.get("/sessions/{session_id}/statistics", response_model=Dict[str, Any])
async def get_session_statistics(
    session_id: int = Path(..., description="ID sesji"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Pobierz statystyki sesji
    
    Args:
        session_id: ID sesji
        db: Sesja bazy danych
        
    Returns:
        Statystyki sesji (liczba interakcji, tokeny, czas trwania)
        
    Raises:
        HTTPException: Gdy sesja nie istnieje
    """
    try:
        stats = await session_repo.get_session_statistics(db, session_id)
        
        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sesja o ID {session_id} nie została znaleziona"
            )
        
        logger.info(f"API: Pobrano statystyki sesji ID: {session_id}")
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas pobierania statystyk sesji {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas pobierania statystyk"
        )


@router.post("/sessions/demo", response_model=SessionDemo, status_code=status.HTTP_201_CREATED)
async def create_demo_session(
    session_data: Optional[SessionCreateDemo] = None,
    db: AsyncSession = Depends(get_db)
) -> SessionDemo:
    """
    Rozpocznij nową sesję demo bez przypisania do klienta
    
    Użyj tego endpointu dla testów konwersacyjnych i demo aplikacji.
    
    Args:
        session_data: Opcjonalne dane sesji demo
        db: Sesja bazy danych
        
    Returns:
        Utworzona sesja demo
    """
    try:
        # Domyślne dane sesji demo
        if not session_data:
            session_data = SessionCreateDemo(
                notes="Demo conversation session - AI Co-Pilot",
                session_type="demo"
            )
        
        logger.info("🎭 Tworzenie sesji demo (bez klienta)")
        
        # Uproszczone tworzenie sesji demo - zwrócenie podstawowych danych
        from app.models.domain import Session as SessionModel
        
        session = SessionModel(
            client_id=None,  # Demo session without client
            session_type=session_data.session_type or "demo",
            summary=session_data.summary or session_data.notes,
            outcome="demo",
            sentiment_score=5,  # Neutralne dla demo
            potential_score=5   # Neutralne dla demo  
        )
        
        db.add(session)
        await db.commit()
        
        # Pobierz ID natychmiast po commit (bez refresh)
        session_id = session.id
        session_start_time = session.start_time or datetime.utcnow()
        
        logger.info(f"✅ Sesja demo utworzona pomyślnie. ID: {session_id}")
        
        # Zwróć prostą strukturę SessionDemo
        return SessionDemo(
            id=session_id,
            client_id=None,
            start_time=session_start_time,
            end_time=None,
            session_type="demo",
            summary=session_data.summary,
            outcome="demo",
            sentiment_score=5,
            potential_score=5,
            is_active=True,
            duration_minutes=None
        )
        
    except Exception as e:
        logger.error(f"❌ Błąd podczas tworzenia sesji demo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas tworzenia sesji demo"
        )


@router.get("/sessions/recent", response_model=List[SessionSummary])
async def get_recent_sessions(
    limit: int = Query(10, ge=1, le=50, description="Maksymalna liczba wyników"),
    only_active: bool = Query(False, description="Tylko aktywne sesje"),
    db: AsyncSession = Depends(get_db)
) -> List[SessionSummary]:
    """
    Pobierz ostatnie sesje
    
    Args:
        limit: Maksymalna liczba wyników
        only_active: Czy tylko aktywne
        db: Sesja bazy danych
        
    Returns:
        Lista ostatnich sesji
    """
    try:
        sessions = await session_repo.get_recent_sessions(
            db=db,
            limit=limit,
            only_active=only_active
        )
        
        # Konwertuj do SessionSummary
        summaries = []
        for session in sessions:
            # Pobierz statystyki
            stats = await session_repo.get_session_statistics(db, session.id)
            
            summary = SessionSummary(
                id=session.id,
                client_id=session.client_id,
                client_name=session.client.name if session.client else None,
                start_time=session.start_time,
                end_time=session.end_time,
                duration_minutes=stats.get("duration_minutes"),
                session_type=session.session_type,
                outcome=session.outcome,
                sentiment_score=session.sentiment_score,
                potential_score=session.potential_score,
                interactions_count=stats.get("interactions_count", 0)
            )
            summaries.append(summary)
        
        logger.info(f"API: Pobrano {len(summaries)} ostatnich sesji")
        return summaries
        
    except Exception as e:
        logger.error(f"Błąd podczas pobierania ostatnich sesji: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas pobierania ostatnich sesji"
        )


@router.get("/clients/{client_id}/engagement", response_model=Dict[str, Any])
async def get_client_engagement(
    client_id: int = Path(..., description="ID klienta"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Oblicz zaangażowanie klienta na podstawie jego sesji
    
    Args:
        client_id: ID klienta
        db: Sesja bazy danych
        
    Returns:
        Metryki zaangażowania klienta
        
    Raises:
        HTTPException: Gdy klient nie istnieje
    """
    try:
        # Sprawdź czy klient istnieje
        client = await client_repo.get(db, client_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Klient o ID {client_id} nie został znaleziony"
            )
        
        # Oblicz zaangażowanie
        engagement = await session_repo.calculate_client_engagement(db, client_id)
        
        # Dodaj dane klienta
        engagement["client_name"] = client.name
        engagement["client_archetype"] = client.archetype
        
        logger.info(f"API: Obliczono zaangażowanie klienta ID: {client_id}")
        return engagement
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas obliczania zaangażowania klienta {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas obliczania zaangażowania"
        )
