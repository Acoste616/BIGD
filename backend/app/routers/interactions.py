"""
Router dla endpointów zarządzania interakcjami w sesjach
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.db_utils import PaginationParams
from app.repositories.interaction_repository import InteractionRepository
from app.repositories.session_repository import SessionRepository
from app.schemas.interaction import (
    Interaction,
    InteractionCreate,
    InteractionCreateNested,
    InteractionUpdate,
    InteractionWithFeedback,
    InteractionWithContext,
    InteractionResponse
)
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


# === ENDPOINTY ZAGNIEŻDŻONE POD SESJĄ ===

@router.post("/sessions/{session_id}/interactions/", response_model=Interaction, status_code=status.HTTP_201_CREATED)
async def create_interaction(
    session_id: int = Path(..., description="ID sesji"),
    interaction_data: InteractionCreateNested = ...,
    db: AsyncSession = Depends(get_db)
) -> Interaction:
    """
    🔥 NAJWAŻNIEJSZY ENDPOINT - Utwórz nową interakcję w sesji
    
    To jest główny punkt wejścia dla danych od sprzedawcy.
    Zapisuje input użytkownika i przygotowuje strukturę odpowiedzi AI.
    
    Args:
        session_id: ID sesji
        interaction_data: Dane wejściowe od użytkownika
        db: Sesja bazy danych
        
    Returns:
        Utworzona interakcja z placeholder odpowiedzią AI
        
    Raises:
        HTTPException: Gdy sesja nie istnieje
        
    Note:
        Na tym etapie nie integrujemy z LLM - zwracamy strukturę placeholder.
        W przyszłości tu będzie wywołanie do modelu AI.
    """
    try:
        # Sprawdź czy sesja istnieje
        session = await session_repo.get(db, session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sesja o ID {session_id} nie została znaleziona"
            )
        
        # Utwórz nową interakcję
        new_interaction = await interaction_repo.create_interaction(
            db=db,
            session_id=session_id,
            interaction_data=interaction_data
        )
        
        logger.info(f"API: Utworzono interakcję {new_interaction.id} w sesji {session_id}")
        logger.info(f"User input: '{interaction_data.user_input[:100]}...'")
        
        # Przygotuj odpowiedź
        response = Interaction.model_validate(new_interaction)
        
        # Log dla debugowania
        logger.debug(f"AI Response structure: {new_interaction.ai_response_json}")
        
        return response
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Błąd podczas tworzenia interakcji: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas tworzenia interakcji"
        )


@router.get("/sessions/{session_id}/interactions/", response_model=Dict[str, Any])
async def get_session_interactions(
    session_id: int = Path(..., description="ID sesji"),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Numer strony"),
    page_size: int = Query(20, ge=1, le=100, description="Liczba wyników na stronę"),
    order_by: Optional[str] = Query(None, description="Pole do sortowania"),
    order_desc: bool = Query(False, description="Sortowanie malejące")
) -> Dict[str, Any]:
    """
    Pobierz listę interakcji dla sesji z paginacją
    
    Domyślnie sortowane chronologicznie (od najstarszej).
    
    Args:
        session_id: ID sesji
        db: Sesja bazy danych
        page: Numer strony
        page_size: Rozmiar strony
        order_by: Pole sortowania
        order_desc: Czy sortować malejąco
        
    Returns:
        Lista interakcji z metadanymi paginacji
        
    Raises:
        HTTPException: Gdy sesja nie istnieje
    """
    try:
        # Sprawdź czy sesja istnieje
        session = await session_repo.get(db, session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sesja o ID {session_id} nie została znaleziona"
            )
        
        # Przygotuj parametry paginacji
        pagination = PaginationParams(
            page=page,
            page_size=page_size,
            order_by=order_by,
            order_desc=order_desc
        )
        
        # Pobierz interakcje
        result = await interaction_repo.get_session_interactions(
            db=db,
            session_id=session_id,
            pagination=pagination
        )
        
        # Konwertuj do odpowiedzi
        response = result.dict()
        
        # Konwertuj obiekty Interaction do schematów Pydantic
        response["items"] = [
            Interaction.model_validate(interaction) 
            for interaction in result.items
        ]
        
        # Dodaj informacje o sesji
        response["session"] = {
            "id": session.id,
            "client_id": session.client_id,
            "start_time": session.start_time,
            "is_active": session.end_time is None
        }
        
        logger.info(f"API: Pobrano {len(result.items)} interakcji dla sesji {session_id}")
        return response
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Błąd podczas pobierania interakcji sesji {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas pobierania listy interakcji"
        )


# === ENDPOINTY BEZPOŚREDNIE DLA INTERAKCJI ===

@router.get("/interactions/{interaction_id}", response_model=Interaction)
async def get_interaction(
    interaction_id: int = Path(..., description="ID interakcji"),
    include_feedback: bool = Query(False, description="Czy dołączyć feedback"),
    db: AsyncSession = Depends(get_db)
) -> Interaction:
    """
    Pobierz szczegóły interakcji po ID
    
    Args:
        interaction_id: ID interakcji
        include_feedback: Czy dołączyć listę feedbacków
        db: Sesja bazy danych
        
    Returns:
        Dane interakcji
        
    Raises:
        HTTPException: Gdy interakcja nie istnieje
    """
    try:
        interaction = await interaction_repo.get_interaction(
            db=db,
            interaction_id=interaction_id,
            include_feedback=include_feedback
        )
        
        if not interaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Interakcja o ID {interaction_id} nie została znaleziona"
            )
        
        logger.info(f"API: Pobrano dane interakcji ID: {interaction_id}")
        
        # Wybierz odpowiedni schemat
        if include_feedback:
            return InteractionWithFeedback.model_validate(interaction)
        else:
            return Interaction.model_validate(interaction)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas pobierania interakcji {interaction_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas pobierania danych interakcji"
        )


@router.put("/interactions/{interaction_id}", response_model=Interaction)
async def update_interaction(
    interaction_id: int = Path(..., description="ID interakcji"),
    update_data: InteractionUpdate = ...,
    db: AsyncSession = Depends(get_db)
) -> Interaction:
    """
    Zaktualizuj dane interakcji
    
    Pozwala na edycję typu interakcji i confidence score.
    Głównie używane do poprawek i tagowania.
    
    Args:
        interaction_id: ID interakcji do aktualizacji
        update_data: Nowe dane interakcji
        db: Sesja bazy danych
        
    Returns:
        Zaktualizowana interakcja
        
    Raises:
        HTTPException: Gdy interakcja nie istnieje
    """
    try:
        # Aktualizuj interakcję
        updated_interaction = await interaction_repo.update_interaction(
            db=db,
            interaction_id=interaction_id,
            update_data=update_data
        )
        
        if not updated_interaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Interakcja o ID {interaction_id} nie została znaleziona"
            )
        
        logger.info(f"API: Zaktualizowano interakcję ID: {interaction_id}")
        return Interaction.model_validate(updated_interaction)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas aktualizacji interakcji {interaction_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas aktualizacji interakcji"
        )


@router.delete("/interactions/{interaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interaction(
    interaction_id: int = Path(..., description="ID interakcji"),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Usuń interakcję (wraz z feedbackiem - kaskadowo)
    
    Args:
        interaction_id: ID interakcji do usunięcia
        db: Sesja bazy danych
        
    Raises:
        HTTPException: Gdy interakcja nie istnieje
    """
    try:
        success = await interaction_repo.delete_interaction(db, interaction_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Interakcja o ID {interaction_id} nie została znaleziona"
            )
        
        logger.info(f"API: Usunięto interakcję ID: {interaction_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas usuwania interakcji {interaction_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas usuwania interakcji"
        )


# === DODATKOWE ENDPOINTY ===

@router.get("/interactions/{interaction_id}/statistics", response_model=Dict[str, Any])
async def get_interaction_statistics(
    interaction_id: int = Path(..., description="ID interakcji"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Pobierz statystyki interakcji
    
    Args:
        interaction_id: ID interakcji
        db: Sesja bazy danych
        
    Returns:
        Statystyki interakcji (tokeny, feedback, sygnały)
        
    Raises:
        HTTPException: Gdy interakcja nie istnieje
    """
    try:
        stats = await interaction_repo.get_interaction_statistics(db, interaction_id)
        
        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Interakcja o ID {interaction_id} nie została znaleziona"
            )
        
        logger.info(f"API: Pobrano statystyki interakcji ID: {interaction_id}")
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas pobierania statystyk interakcji {interaction_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas pobierania statystyk"
        )


@router.get("/sessions/{session_id}/interactions/analysis", response_model=Dict[str, Any])
async def analyze_conversation_flow(
    session_id: int = Path(..., description="ID sesji"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Analizuj przebieg konwersacji w sesji
    
    Zwraca timeline sentymentu, potencjału, kluczowe momenty i trendy.
    
    Args:
        session_id: ID sesji
        db: Sesja bazy danych
        
    Returns:
        Kompleksowa analiza przebiegu konwersacji
        
    Raises:
        HTTPException: Gdy sesja nie istnieje
    """
    try:
        # Sprawdź czy sesja istnieje
        session = await session_repo.get(db, session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sesja o ID {session_id} nie została znaleziona"
            )
        
        # Analizuj przebieg
        analysis = await interaction_repo.analyze_conversation_flow(db, session_id)
        
        # Dodaj kontekst sesji
        analysis["session_type"] = session.session_type
        analysis["session_outcome"] = session.outcome
        
        logger.info(f"API: Przeanalizowano przebieg konwersacji dla sesji {session_id}")
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas analizy konwersacji sesji {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas analizy konwersacji"
        )


@router.get("/interactions/recent", response_model=List[Interaction])
async def get_recent_interactions(
    limit: int = Query(20, ge=1, le=100, description="Maksymalna liczba wyników"),
    session_id: Optional[int] = Query(None, description="Filtruj po sesji"),
    db: AsyncSession = Depends(get_db)
) -> List[Interaction]:
    """
    Pobierz ostatnie interakcje
    
    Args:
        limit: Maksymalna liczba wyników
        session_id: Opcjonalny filtr sesji
        db: Sesja bazy danych
        
    Returns:
        Lista ostatnich interakcji
    """
    try:
        interactions = await interaction_repo.get_recent_interactions(
            db=db,
            limit=limit,
            session_id=session_id
        )
        
        # Konwertuj do schematów
        result = [
            Interaction.model_validate(interaction)
            for interaction in interactions
        ]
        
        logger.info(f"API: Pobrano {len(result)} ostatnich interakcji")
        return result
        
    except Exception as e:
        logger.error(f"Błąd podczas pobierania ostatnich interakcji: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas pobierania ostatnich interakcji"
        )
