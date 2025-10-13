"""
Session Orchestrator Service

Cel:
- Spójna, szybka orkiestracja analizy psychometrycznej sesji (Fast/Slow Path)
- Aktualizacja pól na poziomie `sessions` (cumulative_psychology, customer_archetype, sales_indicators itp.)
- Obsługa pętli doprecyzowań (clarifying questions)

Integracje:
- PsychologyService (Big Five, DISC, Schwartz)
- HolisticSynthesisService (DNA Klienta + wskaźniki sprzedażowe)

Uwaga: Utrzymujemy prosty kontrakt, aby odblokować brakujące importy
i stabilnie uruchomić system zgodnie z whitepaperem.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import Session as SessionModel, Interaction, Client
from app.services.ai import (
    get_psychology_service,
    get_holistic_synthesis_service,
)


logger = logging.getLogger(__name__)


class SessionOrchestratorService:
    """
    Orchestruje analizę psychometryczną sesji i aktualizuje stan w bazie.
    """

    def __init__(self) -> None:
        self.psychology_service = get_psychology_service()
        self.holistic_service = get_holistic_synthesis_service()
        logger.info("✅ SessionOrchestratorService initialized")

    async def orchestrate_psychology_analysis(
        self, session_id: int, db: AsyncSession, ai_service: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Główna analiza psychometryczna sesji (Slow Path):
        - Zbiera historię interakcji
        - Generuje profil psychometryczny
        - Tworzy DNA Klienta i wskaźniki sprzedażowe
        - Aktualizuje rekord `sessions`

        Returns: słownik ze znormalizowanymi danymi dla warstwy API/UX
        """
        # 1) Pobierz sesję i klienta
        session = await db.get(SessionModel, session_id)
        if not session:
            logger.warning(f"⚠️ Session {session_id} not found - returning fallback profile")
            return self._create_minimal_session_profile()

        client: Optional[Client] = await db.get(Client, session.client_id) if session.client_id else None

        # 2) Historia interakcji (ostatnie N → całość jest ok; sort po czasie)
        interactions_result = await db.execute(
            select(Interaction)
            .where(Interaction.session_id == session_id)
            .order_by(Interaction.timestamp.asc())
        )
        interactions: List[Interaction] = interactions_result.scalars().all()

        conversation_history: List[Dict[str, Any]] = []
        for it in interactions:
            conversation_history.append(
                {
                    "user_input": (it.user_input or "").strip(),
                    "ai_response": it.ai_response_json or {},
                    "timestamp": it.timestamp.isoformat() if it.timestamp else None,
                }
            )

        # 3) Analiza psychometryczna
        client_context = {
            "alias": getattr(client, "alias", None),
            "archetype": getattr(client, "archetype", None),
            "notes": getattr(client, "notes", None),
        }

        psychology_profile = await self.psychology_service.generate_psychometric_analysis(
            conversation_history=conversation_history,
            additional_context={"client_profile": client_context, "session_id": session_id},
        )

        psychology_confidence = int(psychology_profile.get("confidence", 0) or 0)

        # 4) DNA Klienta (holistyczna synteza)
        try:
            holistic_profile = await self.holistic_service.run_holistic_synthesis(
                raw_psychology_profile=psychology_profile,
                additional_context={
                    "client_profile": client_context,
                    "session_context": {"type": getattr(session, "session_type", "consultation"), "session_id": session_id},
                },
            )
        except Exception as e:
            logger.error(f"❌ Holistic synthesis error: {e}")
            holistic_profile = self.holistic_service._create_holistic_fallback()

        # 5) Wskaźniki sprzedażowe (z DNA Klienta)
        try:
            sales_indicators = await self.holistic_service.run_sales_indicators_generation(
                holistic_profile=holistic_profile,
                session_context={"type": getattr(session, "session_type", "consultation"), "session_id": session_id},
            )
        except Exception as e:
            logger.error(f"❌ Sales indicators error: {e}")
            sales_indicators = self.holistic_service._create_indicators_fallback()

        # 6) Archetyp (wykorzystaj PsychologyService)
        try:
            customer_archetype = await self.psychology_service.generate_customer_archetype(psychology_profile)
        except Exception as e:
            logger.error(f"❌ Archetype generation error: {e}")
            customer_archetype = self.psychology_service._create_archetype_fallback()

        # 7) Aktualizacja rekordów sesji w DB
        await db.execute(
            update(SessionModel)
            .where(SessionModel.id == session_id)
            .values(
                cumulative_psychology=psychology_profile,
                psychology_confidence=psychology_confidence,
                customer_archetype=customer_archetype,
                sales_indicators=sales_indicators,
                holistic_psychometric_profile=holistic_profile,
                active_clarifying_questions=psychology_profile.get("clarifying_questions", []),
                psychology_updated_at=datetime.utcnow(),
            )
        )

        # 8) Zwróć zunifikowany profil dla warstwy API/UX
        unified = {
            "cumulative_psychology": psychology_profile,
            "customer_archetype": customer_archetype,
            "psychology_confidence": psychology_confidence,
            "sales_indicators": sales_indicators,
            "active_clarifying_questions": psychology_profile.get("clarifying_questions", []),
            "analysis_timestamp": psychology_profile.get("analysis_timestamp"),
            "tesla_archetype_active": bool(customer_archetype.get("archetype_name")) if isinstance(customer_archetype, dict) else False,
            "interaction_count": len(conversation_history),
        }

        logger.info(
            f"✅ Session {session_id} psychology orchestrated | confidence={psychology_confidence}% | interactions={len(conversation_history)}"
        )
        return unified

    async def answer_clarifying_question(
        self, session_id: int, question_id: str, answer: str, db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Przetwarza odpowiedź sprzedawcy na pytanie pomocnicze i aktualizuje sesję.
        - Usuwa pytanie z listy aktywnych
        - Re-uruchamia analizę (lekko) z dodatkowym kontekstem
        """
        session = await db.get(SessionModel, session_id)
        if not session:
            raise ValueError(f"Sesja {session_id} nie istnieje")

        current_questions = list(getattr(session, "active_clarifying_questions", []) or [])
        remaining_questions = [q for q in current_questions if (isinstance(q, dict) and q.get("id") != question_id)]

        # Zapisz zaktualizowaną listę pytań
        await db.execute(
            update(SessionModel)
            .where(SessionModel.id == session_id)
            .values(active_clarifying_questions=remaining_questions)
        )

        # Prosty re-run pełnej analizy – wystarczające dla v1
        try:
            updated = await self.orchestrate_psychology_analysis(session_id=session_id, db=db, ai_service=None)
        except Exception as e:
            logger.error(f"❌ Clarifying answer processing error: {e}")
            updated = self._create_minimal_session_profile()

        # Dołącz podstawowe metadane odpowiedzi
        updated["clarifying_update"] = {
            "question_id": question_id,
            "answer": answer,
            "processed_at": datetime.utcnow().isoformat(),
            "remaining_questions": len(remaining_questions),
        }

        return updated

    def _create_minimal_session_profile(self) -> Dict[str, Any]:
        """Minimalny fallback profil dla sesji."""
        return {
            "cumulative_psychology": {},
            "customer_archetype": {"archetype_name": "Analiza w toku", "confidence": 0},
            "psychology_confidence": 0,
            "sales_indicators": {},
            "active_clarifying_questions": [],
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "tesla_archetype_active": False,
            "interaction_count": 0,
        }


# Singleton instance (używany przez routery i serwisy)
session_orchestrator_service = SessionOrchestratorService()
