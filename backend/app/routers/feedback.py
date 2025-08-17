"""
Router dla endpointów zarządzania ocenami (feedback) interakcji
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.feedback_repository import FeedbackRepository
from app.repositories.interaction_repository import InteractionRepository
from app.schemas.feedback import (
    Feedback,
    FeedbackCreate,
    FeedbackUpdate,
    FeedbackWithInteraction,
    FeedbackSummary,
    FeedbackAnalytics
)
import logging

logger = logging.getLogger(__name__)

# Inicjalizacja routera
router = APIRouter(
    tags=["feedback"],
    responses={
        404: {"description": "Feedback nie znaleziony"},
        400: {"description": "Nieprawidłowe dane wejściowe"}
    }
)

# Inicjalizacja repozytoriów
feedback_repo = FeedbackRepository()
interaction_repo = InteractionRepository()


# === ENDPOINTY ZAGNIEŻDŻONE POD INTERAKCJĄ ===

@router.post("/interactions/{interaction_id}/feedback/", response_model=Feedback, status_code=status.HTTP_201_CREATED)
async def create_feedback(
    interaction_id: int = Path(..., description="ID interakcji"),
    feedback_data: FeedbackCreate = ...,
    db: AsyncSession = Depends(get_db)
) -> Feedback:
    """
    Utwórz nową ocenę dla interakcji
    
    Kluczowy mechanizm zbierania danych do doskonalenia AI.
    Pozwala użytkownikom ocenić jakość sugestii (+1/-1).
    
    Args:
        interaction_id: ID interakcji do oceny
        feedback_data: Dane oceny (rating, opcjonalny komentarz)
        db: Sesja bazy danych
        
    Returns:
        Utworzona ocena
        
    Raises:
        HTTPException: Gdy interakcja nie istnieje
        
    Note:
        System automatycznie analizuje trendy feedbacku
        i aktualizuje metryki AI.
    """
    try:
        # Sprawdź czy interakcja istnieje
        interaction = await interaction_repo.get(db, interaction_id)
        if not interaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Interakcja o ID {interaction_id} nie została znaleziona"
            )
        
        # Utwórz feedback
        new_feedback = await feedback_repo.create_feedback(
            db=db,
            interaction_id=interaction_id,
            feedback_data=feedback_data
        )
        
        logger.info(f"API: Utworzono feedback {new_feedback.id} dla interakcji {interaction_id}")
        
        # Log dla analizy
        if feedback_data.rating == -1:
            logger.warning(f"Negatywny feedback dla interakcji {interaction_id}: {feedback_data.comment}")
        
        return Feedback.model_validate(new_feedback)
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Błąd podczas tworzenia feedbacku: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas tworzenia oceny"
        )


@router.get("/interactions/{interaction_id}/feedback/", response_model=List[Feedback])
async def get_interaction_feedback(
    interaction_id: int = Path(..., description="ID interakcji"),
    db: AsyncSession = Depends(get_db)
) -> List[Feedback]:
    """
    Pobierz wszystkie oceny dla danej interakcji
    
    Args:
        interaction_id: ID interakcji
        db: Sesja bazy danych
        
    Returns:
        Lista ocen dla interakcji
        
    Raises:
        HTTPException: Gdy interakcja nie istnieje
    """
    try:
        # Sprawdź czy interakcja istnieje
        interaction = await interaction_repo.get(db, interaction_id)
        if not interaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Interakcja o ID {interaction_id} nie została znaleziona"
            )
        
        # Pobierz feedbacki
        feedbacks = await feedback_repo.get_interaction_feedback(db, interaction_id)
        
        # Konwertuj do schematów
        result = [
            Feedback.model_validate(feedback)
            for feedback in feedbacks
        ]
        
        logger.info(f"API: Pobrano {len(result)} ocen dla interakcji {interaction_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas pobierania feedbacku interakcji {interaction_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas pobierania ocen"
        )


# === ENDPOINTY BEZPOŚREDNIE DLA FEEDBACKU ===

@router.put("/feedback/{feedback_id}", response_model=Feedback)
async def update_feedback(
    feedback_id: int = Path(..., description="ID feedbacku"),
    update_data: FeedbackUpdate = ...,
    db: AsyncSession = Depends(get_db)
) -> Feedback:
    """
    Zaktualizuj istniejącą ocenę
    
    Pozwala na zmianę ratingu, dodanie komentarza lub oznaczenie zastosowania.
    
    Args:
        feedback_id: ID feedbacku do aktualizacji
        update_data: Nowe dane feedbacku
        db: Sesja bazy danych
        
    Returns:
        Zaktualizowany feedback
        
    Raises:
        HTTPException: Gdy feedback nie istnieje
    """
    try:
        # Aktualizuj feedback
        updated_feedback = await feedback_repo.update_feedback(
            db=db,
            feedback_id=feedback_id,
            update_data=update_data
        )
        
        if not updated_feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feedback o ID {feedback_id} nie został znaleziony"
            )
        
        logger.info(f"API: Zaktualizowano feedback ID: {feedback_id}")
        return Feedback.model_validate(updated_feedback)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas aktualizacji feedbacku {feedback_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas aktualizacji oceny"
        )


@router.delete("/feedback/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feedback(
    feedback_id: int = Path(..., description="ID feedbacku"),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Usuń ocenę
    
    Args:
        feedback_id: ID feedbacku do usunięcia
        db: Sesja bazy danych
        
    Raises:
        HTTPException: Gdy feedback nie istnieje
    """
    try:
        success = await feedback_repo.delete_feedback(db, feedback_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feedback o ID {feedback_id} nie został znaleziony"
            )
        
        logger.info(f"API: Usunięto feedback ID: {feedback_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas usuwania feedbacku {feedback_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas usuwania oceny"
        )


# === DODATKOWE ENDPOINTY ANALITYCZNE ===

@router.get("/feedback/statistics", response_model=Dict[str, Any])
async def get_feedback_statistics(
    entity_type: str = Query("global", description="Typ encji (global/session/client)"),
    entity_id: Optional[int] = Query(None, description="ID encji"),
    time_period: Optional[int] = Query(None, description="Okres czasu w dniach"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Pobierz statystyki feedbacku
    
    Kompleksowa analiza ocen użytkowników.
    
    Args:
        entity_type: Typ analizy (global, session, client)
        entity_id: ID encji dla session/client
        time_period: Okres analizy w dniach
        db: Sesja bazy danych
        
    Returns:
        Statystyki feedbacku z metrykami i analizą
    """
    try:
        stats = await feedback_repo.get_feedback_statistics(
            db=db,
            entity_type=entity_type,
            entity_id=entity_id,
            time_period=time_period
        )
        
        logger.info(f"API: Pobrano statystyki feedbacku dla {entity_type} (ID: {entity_id})")
        return stats
        
    except Exception as e:
        logger.error(f"Błąd podczas pobierania statystyk feedbacku: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas pobierania statystyk"
        )


@router.get("/feedback/problematic-interactions", response_model=List[Dict[str, Any]])
async def get_problematic_interactions(
    threshold: int = Query(-2, description="Próg sumy ocen"),
    limit: int = Query(10, ge=1, le=50, description="Maksymalna liczba wyników"),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Znajdź interakcje z najbardziej negatywnym feedbackiem
    
    Identyfikacja problemów do analizy i poprawy.
    
    Args:
        threshold: Próg sumy ocen (domyślnie -2)
        limit: Maksymalna liczba wyników
        db: Sesja bazy danych
        
    Returns:
        Lista problematycznych interakcji
    """
    try:
        problematic = await feedback_repo.get_problematic_interactions(
            db=db,
            threshold=threshold,
            limit=limit
        )
        
        logger.info(f"API: Znaleziono {len(problematic)} problematycznych interakcji")
        return problematic
        
    except Exception as e:
        logger.error(f"Błąd podczas wyszukiwania problematycznych interakcji: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas wyszukiwania"
        )


@router.get("/feedback/improvement-suggestions", response_model=Dict[str, Any])
async def get_improvement_suggestions(
    session_id: Optional[int] = Query(None, description="ID sesji dla kontekstu"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generuj sugestie poprawy na podstawie feedbacku
    
    Analiza feedbacku i rekomendacje doskonalenia AI.
    
    Args:
        session_id: Opcjonalny ID sesji dla kontekstu
        db: Sesja bazy danych
        
    Returns:
        Sugestie poprawy i obszary do rozwoju
    """
    try:
        suggestions = await feedback_repo.get_improvement_suggestions(
            db=db,
            session_id=session_id
        )
        
        logger.info(f"API: Wygenerowano sugestie poprawy (sesja: {session_id})")
        return suggestions
        
    except Exception as e:
        logger.error(f"Błąd podczas generowania sugestii: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas generowania sugestii"
        )


@router.get("/feedback/ai-performance", response_model=Dict[str, Any])
async def get_ai_performance_metrics(
    time_period: int = Query(30, ge=1, le=365, description="Okres w dniach"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Oblicz metryki wydajności AI na podstawie feedbacku
    
    Kompleksowa ocena jakości odpowiedzi AI.
    
    Args:
        time_period: Okres analizy w dniach
        db: Sesja bazy danych
        
    Returns:
        Metryki wydajności AI z trendem i quality score
    """
    try:
        metrics = await feedback_repo.calculate_ai_performance_metrics(
            db=db,
            time_period=time_period
        )
        
        logger.info(f"API: Obliczono metryki wydajności AI za {time_period} dni")
        return metrics
        
    except Exception as e:
        logger.error(f"Błąd podczas obliczania metryk AI: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas obliczania metryk"
        )
