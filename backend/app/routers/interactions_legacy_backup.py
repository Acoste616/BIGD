"""
Router dla endpointów zarządzania interakcjami - uproszczona wersja
"""
from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.interaction_repository import InteractionRepository
from app.repositories.session_repository import SessionRepository
from app.services.session_psychology_service import session_psychology_engine
from app.schemas.interaction import Interaction, InteractionCreateNested, ClarifyingQuestion
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


@router.post("/interactions/{interaction_id}/clarify", status_code=status.HTTP_201_CREATED)
async def clarify_interaction(
    clarifying_answer: Dict[str, str],
    interaction_id: int = Path(..., description="ID interakcji bazowej"),
    db: AsyncSession = Depends(get_db)
):
    """
    NOWY ENDPOINT: Odpowiedź na pytanie pomocnicze AI
    
    Krok 3 w Interactive Psychometric Flow:
    Sprzedawca odpowiada na pytanie pomocnicze AI i system 
    natychmiast aktualizuje analizę psychometryczną.
    """
    try:
        # Sprawdź czy parent interaction istnieje
        parent_interaction = await interaction_repo.get_interaction(db, interaction_id)
        if not parent_interaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Interakcja bazowa {interaction_id} nie została znaleziona"
            )
        
        # Przygotuj dane dla clarification interaction
        clarification_data = InteractionCreateNested(
            user_input=f"Odpowiedź na pytanie pomocnicze: {clarifying_answer.get('selected_option', '')}",
            interaction_type="clarification",
            additional_context={"clarifying_answer": clarifying_answer},
            clarifying_answer=clarifying_answer,
            parent_interaction_id=interaction_id
        )
        
        # Utwórz clarification interaction
        session_id = int(str(parent_interaction.session_id))  # Explicit conversion via string
        clarification_interaction = await interaction_repo.create_interaction(
            db, session_id, clarification_data
        )
        
        logger.info(f"API: Utworzono clarification interaction {clarification_interaction.id} dla parent {interaction_id}")
        
        return {
            "clarification_interaction": clarification_interaction,
            "parent_interaction_id": interaction_id,
            "message": "Odpowiedź zarejestrowana. Analiza psychometryczna zostanie zaktualizowana w tle.",
            "estimated_update_time": "15-30 sekund"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas przetwarzania clarification dla interakcji {interaction_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas przetwarzania odpowiedzi na pytanie pomocnicze"
        )


@router.post("/sessions/{session_id}/answer_question", status_code=status.HTTP_200_OK)
async def answer_session_question(
    session_question_data: Dict[str, str],
    session_id: int = Path(..., description="ID sesji"),
    db: AsyncSession = Depends(get_db)
):
    """
    NOWY ENDPOINT v3.0: Odpowiedź na pytanie pomocnicze na poziomie SESJI
    
    ETAP 3: Unifikacja Pytań - wykorzystuje SessionPsychologyEngine
    Sprzedawca odpowiada na pytanie pomocnicze i system aktualizuje
    cumulative psychology całej sesji.
    
    Body format:
    {
        "question_id": "sq_1", 
        "answer": "Tak, potwierdza"
    }
    """
    try:
        question_id = session_question_data.get('question_id')
        answer = session_question_data.get('answer')
        
        if not question_id or not answer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Wymagane: question_id i answer"
            )
        
        # Sprawdź czy sesja istnieje
        session = await session_repo.get_session(db, session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sesja o ID {session_id} nie została znaleziona"
            )
        
        logger.info(f"API: Przetwarzam odpowiedź na pytanie {question_id} dla sesji {session_id}: {answer}")
        
        # Wywołaj SessionPsychologyEngine
        updated_profile = await session_psychology_engine.answer_clarifying_question(
            session_id=session_id,
            question_id=question_id, 
            answer=answer,
            db=db
        )
        
        # Pobierz zaktualizowaną sesję dla response
        updated_session = await session_repo.get_session(db, session_id)
        
        return {
            "message": "Odpowiedź przetworzona pomyślnie",
            "session_id": session_id,
            "question_id": question_id,
            "answer": answer,
            "updated_psychology": {
                "confidence": int(updated_session.psychology_confidence) if updated_session.psychology_confidence else 0,
                "active_questions_count": len(list(updated_session.active_clarifying_questions) if updated_session.active_clarifying_questions else []),
                "archetype": updated_session.customer_archetype.get('archetype_name', 'Analiza w toku') if updated_session.customer_archetype else 'Analiza w toku'
            },
            "estimated_analysis_time": "5-15 sekund"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas przetwarzania odpowiedzi na pytanie sesji {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas przetwarzania odpowiedzi na pytanie pomocnicze"
        )