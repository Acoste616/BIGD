"""
Router dla endpointów zarządzania interakcjami - REFAKTORYZACJA v2.0

ARCHITEKTURA WARSTWOWA - NAPRAWIONA:
❌ PRZED: Router → Repository (150+ linii AI logiki w DB layer)  
✅ PO: Router → Service → Repository (clean separation of concerns)

Zmiany:
✅ InteractionService: Obsługuje całą logikę biznesową i AI
✅ InteractionRepository: Tylko czyste operacje DB
✅ Clean Architecture: Proper layering restored
"""
from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.interaction_service import get_interaction_service
from app.repositories.session_repository import SessionRepository
from app.services.session_orchestrator_service import session_orchestrator_service
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

# === DEPENDENCY INJECTION - NOWA ARCHITEKTURA ===

# Service Layer - główna logika biznesowa
def get_interaction_service_dependency():
    """Dependency injection dla InteractionService"""
    return get_interaction_service()

# Repository Layer - tylko sesje (interakcje obsługuje już serwis)
session_repo = SessionRepository()


# === MAIN ENDPOINTS - REFAKTORYZOWANE ===

@router.post("/sessions/{session_id}/interactions/", status_code=status.HTTP_201_CREATED)
async def create_interaction(
    interaction_data: InteractionCreateNested,
    session_id: int = Path(..., description="ID sesji"),
    db: AsyncSession = Depends(get_db),
    interaction_service = Depends(get_interaction_service_dependency)
):
    """
    REFAKTORYZACJA: Utwórz nową interakcję z AI analysis przez Service Layer
    
    PRZED: Router → Repository (150+ linii AI logiki w DB layer)
    PO: Router → InteractionService → Repository (clean architecture)
    """
    try:
        # NOWA ARCHITEKTURA: Service obsługuje walidację i logikę biznesową
        new_interaction = await interaction_service.create_interaction_with_ai_analysis(
            db=db,
            session_id=session_id, 
            interaction_data=interaction_data
        )
        
        logger.info(f"✅ [ROUTER] Interaction {new_interaction.id} created via Service Layer")
        return new_interaction
        
    except ValueError as e:
        # Service rzuca ValueError dla business logic errors
        logger.error(f"❌ [ROUTER] Business logic error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Nieoczekiwane błędy
        logger.error(f"❌ [ROUTER] Unexpected error creating interaction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas tworzenia interakcji"
        )


@router.get("/sessions/{session_id}/interactions/")
async def get_session_interactions(
    session_id: int = Path(..., description="ID sesji"),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="Liczba interakcji do pominięcia"),
    limit: int = Query(100, ge=1, le=1000, description="Maksymalna liczba interakcji"),
    interaction_service = Depends(get_interaction_service_dependency)
):
    """
    Pobierz interakcje dla sesji - delegacja do Service
    """
    try:
        # Sprawdź czy sesja istnieje (można przenieść do Service jeśli potrzeba)
        session = await session_repo.get_session(db, session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sesja o ID {session_id} nie została znaleziona"
            )
        
        # NOWA ARCHITEKTURA: Service deleguje do Repository
        interactions = await interaction_service.get_session_interactions(db, session_id, skip, limit)
        
        logger.info(f"✅ [ROUTER] Retrieved {len(interactions)} interactions for session {session_id}")
        return interactions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [ROUTER] Error retrieving interactions for session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas pobierania interakcji"
        )


@router.get("/interactions/{interaction_id}")
async def get_interaction(
    interaction_id: int = Path(..., description="ID interakcji"),
    db: AsyncSession = Depends(get_db),
    interaction_service = Depends(get_interaction_service_dependency)
):
    """
    Pobierz szczegóły interakcji - delegacja do Service
    """
    try:
        interaction = await interaction_service.get_interaction(db, interaction_id)
        
        if not interaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Interakcja o ID {interaction_id} nie została znaleziona"
            )
        
        logger.info(f"✅ [ROUTER] Retrieved interaction {interaction_id}")
        return interaction
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [ROUTER] Error retrieving interaction {interaction_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas pobierania szczegółów interakcji"
        )


# === ADVANCED ENDPOINTS - PSYCHOLOGY INTEGRATION ===

@router.post("/interactions/{interaction_id}/clarify", status_code=status.HTTP_201_CREATED)
async def clarify_interaction(
    clarifying_answer: Dict[str, str],
    interaction_id: int = Path(..., description="ID interakcji bazowej"),
    db: AsyncSession = Depends(get_db),
    interaction_service = Depends(get_interaction_service_dependency)
):
    """
    REFAKTORYZACJA: Odpowiedź na pytanie pomocnicze AI przez Service Layer
    
    Tworzy clarification interaction z full AI analysis pipeline
    """
    try:
        # Sprawdź czy parent interaction istnieje - delegacja do Service  
        parent_interaction = await interaction_service.get_interaction(db, interaction_id)
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
        
        # NOWA ARCHITEKTURA: Service obsługuje całą logikę clarification
        session_id = parent_interaction.session_id
        clarification_interaction = await interaction_service.create_interaction_with_ai_analysis(
            db=db,
            session_id=session_id,
            interaction_data=clarification_data
        )
        
        logger.info(f"✅ [ROUTER] Clarification interaction {clarification_interaction.id} created for parent {interaction_id}")
        
        return {
            "clarification_interaction": clarification_interaction,
            "parent_interaction_id": interaction_id,
            "message": "Odpowiedź zarejestrowana. Analiza psychometryczna zostanie zaktualizowana w tle.",
            "estimated_update_time": "15-30 sekund"
        }
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"❌ [ROUTER] Business error in clarification: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ [ROUTER] Error processing clarification for interaction {interaction_id}: {e}")
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
    Odpowiedź na pytanie pomocnicze na poziomie SESJI
    
    UWAGA: Ten endpoint używa session_psychology_engine bezpośrednio
    Można rozważyć przeniesienie tej logiki do Service Layer w przyszłości
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
        
        logger.info(f"📋 [ROUTER] Processing session question {question_id} for session {session_id}: {answer}")
        
        # TYMCZASOWO: Bezpośrednie wywołanie SessionPsychologyEngine
        # TODO: Przenieść do SessionService jeśli zostanie stworzony
        updated_profile = await session_orchestrator_service.answer_clarifying_question(
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
                "confidence": int(getattr(updated_session, 'psychology_confidence', 0) or 0) if updated_session else 0,
                "active_questions_count": len(getattr(updated_session, 'active_clarifying_questions', None) or []) if updated_session else 0,
                "archetype": (getattr(updated_session, 'customer_archetype', None) or {}).get('archetype_name', 'Analiza w toku') if updated_session else 'Analiza w toku'
            },
            "estimated_analysis_time": "5-15 sekund"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [ROUTER] Error processing session question for {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas przetwarzania odpowiedzi na pytanie pomocnicze"
        )


# === UTILITY ENDPOINTS ===

@router.get("/interactions/{interaction_id}/health")
async def get_interaction_health(
    interaction_id: int = Path(..., description="ID interakcji"),
    db: AsyncSession = Depends(get_db),
    interaction_service = Depends(get_interaction_service_dependency)
):
    """
    NOWY ENDPOINT: Health check dla konkretnej interakcji
    """
    try:
        interaction = await interaction_service.get_interaction(db, interaction_id)
        
        if not interaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Interakcja {interaction_id} nie została znaleziona"
            )
        
        # Sprawdź health AI response
        ai_response = interaction.ai_response_json or {}
        
        health_status = {
            "interaction_id": interaction_id,
            "exists": True,
            "has_ai_response": bool(ai_response),
            "ai_response_type": "fallback" if ai_response.get("is_fallback") else "full_analysis",
            "user_input_length": len(interaction.user_input) if interaction.user_input else 0,
            "timestamp": interaction.timestamp.isoformat() if interaction.timestamp else None
        }
        
        return health_status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [ROUTER] Error checking interaction {interaction_id} health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas sprawdzania stanu interakcji"
        )


@router.get("/service/health")
async def get_service_health(
    interaction_service = Depends(get_interaction_service_dependency)
):
    """
    NOWY ENDPOINT: Health check dla InteractionService i connected AI services
    """
    try:
        service_status = interaction_service.get_service_status()
        return service_status
        
    except Exception as e:
        logger.error(f"❌ [ROUTER] Error getting service health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas sprawdzania stanu serwisu"
        )


# === LEGACY COMPATIBILITY (do usunięcia w przyszłości) ===

@router.post("/sessions/{session_id}/interactions/legacy", status_code=status.HTTP_201_CREATED)
async def create_interaction_legacy(
    interaction_data: InteractionCreateNested,
    session_id: int = Path(..., description="ID sesji"),
    db: AsyncSession = Depends(get_db),
    interaction_service = Depends(get_interaction_service_dependency)
):
    """
    LEGACY ENDPOINT: Fallback dla starych wywołań
    
    ⚠️ DEPRECATED: Użyj /sessions/{session_id}/interactions/
    """
    logger.warning("⚠️ [ROUTER] Using LEGACY endpoint - should migrate to main endpoint")
    
    # Redirect do nowego endpointu
    return await create_interaction(interaction_data, session_id, db, interaction_service)
