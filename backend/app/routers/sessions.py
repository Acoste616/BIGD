"""
Router dla endpointów zarządzania sesjami - uproszczona wersja
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.repositories.session_repository import SessionRepository
from app.repositories.client_repository import ClientRepository
from app.schemas.session import Session, SessionCreate, SessionCreateNested
from app.models.domain import Interaction
from app.services.session_orchestrator_service import session_orchestrator_service
from app.services.ai_service import get_ai_service
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


@router.get("/sessions/{session_id}/analytics")
async def get_session_analytics(
    session_id: int = Path(..., description="ID sesji"),
    db: AsyncSession = Depends(get_db)
):
    """
    Pobierz dane analityczne dla sesji (PRL, FDS, summary, dominant_traits, psychology_profile)
    """
    try:
        # Pobierz sesję używając repository
        session = await session_repo.get_session(db, session_id)

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sesja o ID {session_id} nie została znaleziona"
            )

        # Policz interakcje
        interactions_query = select(func.count(Interaction.id)).where(Interaction.session_id == session_id)
        interactions_result = await db.execute(interactions_query)
        interactions_count = interactions_result.scalar() or 0

        # 🧠⚡ INTEGRACJA Z ULTRA MÓZGEM: Wywołaj SessionPsychologyEngine
        logger.info(f"🧠⚡ [ANALYTICS] Wywołuję SessionPsychologyEngine dla sesji {session_id}")
        ai_service = get_ai_service()
        if not ai_service:
            logger.warning("🧠⚡ [ANALYTICS] AIService nie jest zainicjalizowany, używam fallback")
            # Fallback dla przypadku gdy AIService nie jest dostępny - create minimal profile
            psychology_profile = {
                'cumulative_psychology': {},
                'customer_archetype': {'archetype_key': 'neutral', 'confidence': 10},
                'psychology_confidence': 10,
                'sales_indicators': {},
                'active_clarifying_questions': [],
                'analysis_timestamp': datetime.now().isoformat(),
                'tesla_archetype_active': False,
                'analysis_level': 'wstępna',
                'interaction_count': 0
            }
        else:
            psychology_profile = await session_orchestrator_service.orchestrate_psychology_analysis(session_id, db, ai_service)

        # Wyciągnij dane z profilu psychometrycznego
        cumulative_psychology = psychology_profile.get('cumulative_psychology', {})
        customer_archetype = psychology_profile.get('customer_archetype', {})
        psychology_confidence = psychology_profile.get('psychology_confidence', 0)
        sales_indicators = psychology_profile.get('sales_indicators', {})

        # Przygotuj dane PRL na podstawie profilu psychometrycznego
        prl_data = {
            "value": psychology_confidence,
            "level": "high" if psychology_confidence >= 70 else "medium" if psychology_confidence >= 40 else "low",
            "description": f"Analiza psychometryczna wykonana z pewnością {psychology_confidence}%"
        }

        # Przygotuj dane FDS na podstawie sales_indicators
        purchase_temperature = sales_indicators.get('purchase_temperature', {})
        fds_data = {
            "stage": sales_indicators.get('customer_journey_stage', {}).get('value', 'gathering_info'),
            "confidence": purchase_temperature.get('confidence', 0),
            "estimated_value": sales_indicators.get('sales_potential', {}).get('value', 0),
            "risk_level": sales_indicators.get('churn_risk', {}).get('risk_level', 'unknown')
        }

        # Przygotuj summary na podstawie archetypu i analizy
        archetype_name = customer_archetype.get('archetype_name', 'Nieokreślony')
        archetype_key = customer_archetype.get('archetype_key', 'neutral')

        summary_data = {
            "psychology_summary": f"Klient klasyfikowany jako {archetype_name} z pewnością {customer_archetype.get('confidence', 0)}%",
            "conversation_summary": f"Sesja zawiera {interactions_count} interakcji. Profil psychometryczny: {archetype_key}",
            "last_updated": psychology_profile.get('analysis_timestamp')
        }

        # Wyciągnij dominant_traits z Big Five i DISC
        dominant_traits = []
        big_five = cumulative_psychology.get('big_five', {})

        # Znajdź najbardziej wyraziste cechy Big Five
        for trait, data in big_five.items():
            score = data.get('score', 5)
            if score >= 7:
                dominant_traits.append(data.get('rationale', trait).split(' - ')[0][:20])
            elif score <= 3:
                dominant_traits.append(f"Niski {trait}")

        # Dodaj cechy z archetypu jeśli dostępne
        if customer_archetype.get('key_traits'):
            dominant_traits.extend(customer_archetype['key_traits'][:3])  # Max 3 cechy

        # Fallback dla pustej listy
        if not dominant_traits:
            dominant_traits = ["Analityczność", "Ostrożność"]

        # Przygotuj kompletne dane analityczne z integracją Ultra Mózgu
        analytics_data = {
            "session_id": session_id,
            "client_id": session.client_id,
            "status": session.status,
            "is_active": bool(session.is_active),
            "created_at": session.start_timestamp.isoformat() if session.start_timestamp is not None else None,
            "interaction_count": interactions_count,

            # Klasyczne wskaźniki (zaktualizowane na podstawie profilu psychometrycznego)
            "PRL": prl_data,
            "FDS": fds_data,
            "summary": summary_data,
            "dominant_traits": dominant_traits[:5],  # Max 5 cech

            # 🧠⚡ INTEGRACJA ULTRA MÓZGU: Kompletny profil psychometryczny dla frontendu
            "psychology_profile": psychology_profile,
            "cumulative_psychology": cumulative_psychology,
            "customer_archetype": customer_archetype,
            "sales_indicators": sales_indicators,
            "psychology_confidence": psychology_confidence
        }

        logger.info(f"🧠⚡ [ANALYTICS] Kompletne dane analityczne dla sesji {session_id} z psychology_confidence={psychology_confidence}%")
        return analytics_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [ANALYTICS] Błąd podczas pobierania analityki sesji {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas pobierania danych analitycznych"
        )