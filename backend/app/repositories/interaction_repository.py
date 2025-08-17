"""
Repozytorium dla operacji na interakcjach w sesjach
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload, joinedload

from app.core.db_utils import DatabaseRepository, PaginationParams, PaginatedResponse, paginate
from app.models.domain import Interaction, Session as SessionModel, Feedback, Client
from app.schemas.interaction import InteractionCreate, InteractionCreateNested, InteractionUpdate, InteractionResponse
from app.services.ai_service import generate_sales_analysis
import logging
import json

logger = logging.getLogger(__name__)


class InteractionRepository(DatabaseRepository):
    """
    Repozytorium dla modelu Interaction z rozszerzonymi funkcjonalnościami
    """
    
    def __init__(self):
        super().__init__(Interaction)
    
    async def create_interaction(
        self,
        db: AsyncSession,
        session_id: int,
        interaction_data: InteractionCreateNested
    ) -> Interaction:
        """
        🤖 Utwórz nową interakcję z prawdziwą analizą AI
        
        Args:
            db: Sesja bazy danych
            session_id: ID sesji
            interaction_data: Dane interakcji
            
        Returns:
            Utworzona interakcja z analizą AI
            
        Raises:
            ValueError: Gdy sesja nie istnieje lub jest zakończona
        """
        start_time = datetime.utcnow()
        
        try:
            # 1. Sprawdź czy sesja istnieje i pobierz pełne dane
            session_query = await db.execute(
                select(SessionModel)
                .options(joinedload(SessionModel.client))
                .where(SessionModel.id == session_id)
            )
            session = session_query.scalar_one_or_none()
            
            if not session:
                raise ValueError(f"Sesja o ID {session_id} nie istnieje")
            
            # 2. Reaktywuj sesję jeśli była zakończona
            if session.end_time:
                logger.warning(f"🔄 Reaktywacja zakończonej sesji {session_id}")
                session.end_time = None
                await db.commit()
                logger.info(f"✅ Reaktywowano sesję {session_id} dla nowej interakcji")
            
            # 3. Pobierz profil klienta
            client_profile = self._extract_client_profile(session.client)
            
            # 4. Pobierz historię ostatnich interakcji z sesji
            session_history = await self._get_session_history(db, session_id, limit=5)
            
            # 5. Przygotuj kontekst sesji
            session_context = {
                "session_type": session.session_type,
                "session_id": session_id,
                "start_time": session.start_time.isoformat() if session.start_time else None
            }
            
            # 6. 🤖 WYWOŁAJ PRAWDZIWE AI - główny moment integracji!
            logger.info(f"🤖 Wywołuję AI dla sesji {session_id}: '{interaction_data.user_input[:50]}...'")
            
            ai_response = await generate_sales_analysis(
                user_input=interaction_data.user_input,
                client_profile=client_profile,
                session_history=session_history,
                session_context=session_context
            )
            
            # 7. Przygotuj dane interakcji z prawdziwymi metrykami AI
            processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            interaction_dict = {
                "session_id": session_id,
                "user_input": interaction_data.user_input,
                "interaction_type": interaction_data.interaction_type,
                "timestamp": start_time,
                "ai_response_json": ai_response,
                
                # Prawdziwe metryki z AI
                "confidence_score": ai_response.get("confidence_level", 50),
                "tokens_used": ai_response.get("tokens_used"),  # Może być None, co jest OK
                "processing_time_ms": ai_response.get("processing_time_ms", processing_time),
                
                # Wyekstraktowane dane z AI
                "suggested_actions": ai_response.get("suggested_actions", []),
                "identified_signals": (
                    ai_response.get("buy_signals", []) + 
                    ai_response.get("risk_signals", [])
                ),
                "archetype_match": ai_response.get("client_archetype")
            }
            
            # 8. Utwórz interakcję w bazie danych
            db_interaction = await self.create(db, interaction_dict)
            
            # 9. Zaktualizuj statystyki sesji na podstawie prawdziwej analizy AI
            await self._update_session_stats(db, session, ai_response)
            
            # 10. Loguj sukces
            confidence = ai_response.get("confidence_level", "N/A")
            model_used = ai_response.get("model_used", "unknown")
            
            logger.info(
                f"✅ Utworzono interakcję ID: {db_interaction.id} "
                f"| Sesja: {session_id} | Pewność AI: {confidence}% | Model: {model_used}"
            )
            
            return db_interaction
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"❌ Błąd podczas tworzenia interakcji z AI: {e}")
            
            # W przypadku błędu AI, stwórz interakcję z fallback response
            try:
                fallback_response = await self._create_fallback_interaction(
                    db, session_id, interaction_data, str(e)
                )
                logger.warning(f"🔄 Utworzono interakcję fallback: {fallback_response.id}")
                return fallback_response
            except Exception as fallback_error:
                logger.error(f"💥 Błąd również w fallback: {fallback_error}")
                raise e  # Zwróć pierwotny błąd
    
    def _prepare_ai_response_structure(
        self,
        user_input: str,
        session: SessionModel
    ) -> Dict[str, Any]:
        """
        Przygotuj strukturę odpowiedzi AI (placeholder do integracji z LLM)
        
        Args:
            user_input: Wejście użytkownika
            session: Obiekt sesji
            
        Returns:
            Struktura odpowiedzi AI
        """
        # To jest placeholder - zostanie zastąpiony prawdziwą integracją z AI
        return {
            "main_analysis": f"Analiza: '{user_input[:100]}...' - To jest placeholder odpowiedzi AI.",
            "client_archetype": "Pragmatyczny Analityk",  # Placeholder
            "confidence_level": 85,
            
            "suggested_actions": [
                {"action": "Zapytaj o budżet", "reasoning": "Klient wspomniał o zainteresowaniu"},
                {"action": "Pokaż Model Y", "reasoning": "Pasuje do profilu klienta"},
                {"action": "Omów koszty eksploatacji", "reasoning": "Klient jest analityczny"},
                {"action": "Zaproponuj jazdę testową", "reasoning": "Zwiększ zaangażowanie"}
            ],
            
            "buy_signals": ["zainteresowanie ceną", "pytania o dostępność"],
            "risk_signals": ["wahanie", "porównywanie z konkurencją"],
            
            "key_insights": [
                "Klient jest w fazie rozważania",
                "Potrzebuje więcej danych technicznych",
                "Ważny jest aspekt ekonomiczny"
            ],
            
            "objection_handlers": {
                "za drogo": "Pokaż TCO i oszczędności długoterminowe",
                "zasięg": "Omów realny zasięg i infrastrukturę ładowania"
            },
            
            "qualifying_questions": [
                "Jaki jest Pana główny cel zakupu samochodu elektrycznego?",
                "Czy rozważał Pan leasing czy zakup gotówkowy?",
                "Jakie są Pana dzienne potrzeby transportowe?"
            ],
            
            "sentiment_score": 7,
            "potential_score": 6,
            "urgency_level": "medium",
            
            "next_best_action": "Zaprezentuj konkretną konfigurację Model Y",
            "follow_up_timing": "2-3 dni"
        }
    
    async def _update_session_stats(
        self,
        db: AsyncSession,
        session: SessionModel,
        ai_response: Dict[str, Any]
    ) -> None:
        """
        Zaktualizuj statystyki sesji na podstawie nowej interakcji
        
        Args:
            db: Sesja bazy danych
            session: Obiekt sesji
            ai_response: Odpowiedź AI
        """
        try:
            # Aktualizuj sentiment i potential jeśli są nowe wartości
            if "sentiment_score" in ai_response:
                # Oblicz średnią ważoną (nowa wartość ma większą wagę)
                if session.sentiment_score:
                    session.sentiment_score = int(
                        (session.sentiment_score * 0.7 + ai_response["sentiment_score"] * 0.3)
                    )
                else:
                    session.sentiment_score = ai_response["sentiment_score"]
            
            if "potential_score" in ai_response:
                if session.potential_score:
                    session.potential_score = int(
                        (session.potential_score * 0.7 + ai_response["potential_score"] * 0.3)
                    )
                else:
                    session.potential_score = ai_response["potential_score"]
            
            # Aktualizuj key_facts
            if not session.key_facts:
                session.key_facts = {}
            
            # Dodaj nowe kluczowe informacje
            session.key_facts["last_interaction"] = datetime.utcnow().isoformat()
            session.key_facts["total_interactions"] = session.key_facts.get("total_interactions", 0) + 1
            
            if "client_archetype" in ai_response:
                session.key_facts["identified_archetype"] = ai_response["client_archetype"]
            
            # Aktualizuj risk_indicators
            if ai_response.get("risk_signals"):
                if not session.risk_indicators:
                    session.risk_indicators = {}
                session.risk_indicators["latest_risks"] = ai_response["risk_signals"]
                session.risk_indicators["risk_level"] = self._calculate_risk_level(ai_response["risk_signals"])
            
            await db.commit()
            logger.debug(f"Zaktualizowano statystyki sesji {session.id}")
            
        except Exception as e:
            logger.error(f"Błąd podczas aktualizacji statystyk sesji: {e}")
    
    def _calculate_risk_level(self, risk_signals: List[str]) -> str:
        """
        Oblicz poziom ryzyka na podstawie sygnałów
        
        Args:
            risk_signals: Lista sygnałów ryzyka
            
        Returns:
            Poziom ryzyka (low/medium/high)
        """
        if not risk_signals:
            return "low"
        elif len(risk_signals) <= 2:
            return "medium"
        else:
            return "high"
    
    async def get_interaction(
        self,
        db: AsyncSession,
        interaction_id: int,
        include_feedback: bool = False
    ) -> Optional[Interaction]:
        """
        Pobierz interakcję po ID
        
        Args:
            db: Sesja bazy danych
            interaction_id: ID interakcji
            include_feedback: Czy dołączyć feedback
            
        Returns:
            Interakcja lub None
        """
        query = select(Interaction).where(Interaction.id == interaction_id)
        
        if include_feedback:
            query = query.options(selectinload(Interaction.feedbacks))
        
        result = await db.execute(query)
        interaction = result.scalar_one_or_none()
        
        if interaction:
            logger.debug(f"Pobrano interakcję ID: {interaction_id}")
        else:
            logger.warning(f"Nie znaleziono interakcji o ID: {interaction_id}")
            
        return interaction
    
    async def get_session_interactions(
        self,
        db: AsyncSession,
        session_id: int,
        pagination: PaginationParams
    ) -> PaginatedResponse:
        """
        Pobierz interakcje sesji z paginacją
        
        Args:
            db: Sesja bazy danych
            session_id: ID sesji
            pagination: Parametry paginacji
            
        Returns:
            PaginatedResponse z interakcjami
        """
        # Sprawdź czy sesja istnieje
        session_exists = await db.execute(
            select(SessionModel).where(SessionModel.id == session_id)
        )
        if not session_exists.scalar_one_or_none():
            raise ValueError(f"Sesja o ID {session_id} nie istnieje")
        
        # Podstawowe zapytanie
        query = select(Interaction).where(Interaction.session_id == session_id)
        
        # Domyślne sortowanie - chronologicznie
        if not pagination.order_by:
            query = query.order_by(Interaction.timestamp.asc())
        else:
            if hasattr(Interaction, pagination.order_by):
                order_column = getattr(Interaction, pagination.order_by)
                if pagination.order_desc:
                    query = query.order_by(order_column.desc())
                else:
                    query = query.order_by(order_column.asc())
        
        # Wykonaj z paginacją
        result = await paginate(db, query, pagination)
        
        logger.info(f"Pobrano {len(result.items)} interakcji dla sesji ID: {session_id}")
        return result
    
    async def update_interaction(
        self,
        db: AsyncSession,
        interaction_id: int,
        update_data: InteractionUpdate
    ) -> Optional[Interaction]:
        """
        Zaktualizuj dane interakcji
        
        Args:
            db: Sesja bazy danych
            interaction_id: ID interakcji
            update_data: Dane do aktualizacji
            
        Returns:
            Zaktualizowana interakcja lub None
        """
        interaction = await self.get(db, interaction_id)
        
        if not interaction:
            logger.warning(f"Nie można zaktualizować - interakcja o ID {interaction_id} nie istnieje")
            return None
        
        # Aktualizuj tylko podane pola
        update_dict = update_data.model_dump(exclude_unset=True)
        
        if update_dict:
            updated_interaction = await self.update(db, interaction, update_dict)
            logger.info(f"Zaktualizowano interakcję ID: {interaction_id}")
            return updated_interaction
        else:
            logger.info(f"Brak danych do aktualizacji dla interakcji ID: {interaction_id}")
            return interaction
    
    async def delete_interaction(
        self,
        db: AsyncSession,
        interaction_id: int
    ) -> bool:
        """
        Usuń interakcję (kaskadowo z feedbackiem)
        
        Args:
            db: Sesja bazy danych
            interaction_id: ID interakcji
            
        Returns:
            True jeśli usunięto, False jeśli nie znaleziono
        """
        # Pobierz interakcję aby znać session_id
        interaction = await self.get(db, interaction_id)
        if interaction:
            session_id = interaction.session_id
        
        success = await self.delete(db, interaction_id)
        
        if success:
            logger.info(f"Usunięto interakcję o ID: {interaction_id}")
            
            # Zaktualizuj licznik w sesji
            if interaction:
                await self._decrement_session_counter(db, session_id)
        else:
            logger.warning(f"Nie można usunąć - interakcja o ID {interaction_id} nie istnieje")
            
        return success
    
    async def _decrement_session_counter(
        self,
        db: AsyncSession,
        session_id: int
    ) -> None:
        """
        Zmniejsz licznik interakcji w sesji po usunięciu
        
        Args:
            db: Sesja bazy danych
            session_id: ID sesji
        """
        try:
            session = await db.execute(
                select(SessionModel).where(SessionModel.id == session_id)
            )
            session = session.scalar_one_or_none()
            
            if session and session.key_facts:
                total = session.key_facts.get("total_interactions", 1)
                session.key_facts["total_interactions"] = max(0, total - 1)
                await db.commit()
        except Exception as e:
            logger.error(f"Błąd podczas aktualizacji licznika sesji: {e}")
    
    async def get_interaction_statistics(
        self,
        db: AsyncSession,
        interaction_id: int
    ) -> Dict[str, Any]:
        """
        Pobierz statystyki interakcji
        
        Args:
            db: Sesja bazy danych
            interaction_id: ID interakcji
            
        Returns:
            Słownik ze statystykami
        """
        interaction = await self.get(db, interaction_id)
        if not interaction:
            return {}
        
        # Policz feedback
        positive_feedback = await db.execute(
            select(func.count(Feedback.id))
            .where(and_(
                Feedback.interaction_id == interaction_id,
                Feedback.rating == 1
            ))
        )
        positive = positive_feedback.scalar() or 0
        
        negative_feedback = await db.execute(
            select(func.count(Feedback.id))
            .where(and_(
                Feedback.interaction_id == interaction_id,
                Feedback.rating == -1
            ))
        )
        negative = negative_feedback.scalar() or 0
        
        # Przeanalizuj odpowiedź AI
        ai_response = interaction.ai_response_json or {}
        
        return {
            "interaction_id": interaction_id,
            "session_id": interaction.session_id,
            "timestamp": interaction.timestamp,
            "tokens_used": interaction.tokens_used or 0,
            "processing_time_ms": interaction.processing_time_ms or 0,
            "confidence_score": interaction.confidence_score,
            "positive_feedback": positive,
            "negative_feedback": negative,
            "feedback_score": positive - negative,
            "suggested_actions_count": len(interaction.suggested_actions or []),
            "identified_signals_count": len(interaction.identified_signals or []),
            "archetype_match": interaction.archetype_match,
            "sentiment": ai_response.get("sentiment_score"),
            "potential": ai_response.get("potential_score"),
            "urgency": ai_response.get("urgency_level")
        }
    
    async def get_recent_interactions(
        self,
        db: AsyncSession,
        limit: int = 20,
        session_id: Optional[int] = None
    ) -> List[Interaction]:
        """
        Pobierz ostatnie interakcje
        
        Args:
            db: Sesja bazy danych
            limit: Maksymalna liczba wyników
            session_id: Opcjonalny filtr sesji
            
        Returns:
            Lista ostatnich interakcji
        """
        query = select(Interaction)
        
        if session_id:
            query = query.where(Interaction.session_id == session_id)
        
        query = query.order_by(Interaction.timestamp.desc()).limit(limit)
        
        result = await db.execute(query)
        interactions = result.scalars().all()
        
        logger.info(f"Pobrano {len(interactions)} ostatnich interakcji")
        return interactions
    
    async def analyze_conversation_flow(
        self,
        db: AsyncSession,
        session_id: int
    ) -> Dict[str, Any]:
        """
        Analizuj przebieg konwersacji w sesji
        
        Args:
            db: Sesja bazy danych
            session_id: ID sesji
            
        Returns:
            Analiza przebiegu konwersacji
        """
        # Pobierz wszystkie interakcje sesji
        interactions = await db.execute(
            select(Interaction)
            .where(Interaction.session_id == session_id)
            .order_by(Interaction.timestamp.asc())
        )
        interactions = interactions.scalars().all()
        
        if not interactions:
            return {"error": "Brak interakcji w sesji"}
        
        # Analiza sentymentu w czasie
        sentiment_timeline = []
        potential_timeline = []
        
        for interaction in interactions:
            ai_response = interaction.ai_response_json or {}
            if "sentiment_score" in ai_response:
                sentiment_timeline.append({
                    "timestamp": interaction.timestamp,
                    "value": ai_response["sentiment_score"]
                })
            if "potential_score" in ai_response:
                potential_timeline.append({
                    "timestamp": interaction.timestamp,
                    "value": ai_response["potential_score"]
                })
        
        # Identyfikacja kluczowych momentów
        key_moments = []
        for i, interaction in enumerate(interactions):
            ai_response = interaction.ai_response_json or {}
            
            # Sprawdź skok sentymentu
            if i > 0 and sentiment_timeline:
                if len(sentiment_timeline) > i and len(sentiment_timeline) > i-1:
                    sentiment_change = sentiment_timeline[i]["value"] - sentiment_timeline[i-1]["value"]
                    if abs(sentiment_change) >= 3:
                        key_moments.append({
                            "interaction_id": interaction.id,
                            "timestamp": interaction.timestamp,
                            "type": "sentiment_shift",
                            "change": sentiment_change
                        })
            
            # Identyfikuj ważne sygnały
            if ai_response.get("buy_signals"):
                key_moments.append({
                    "interaction_id": interaction.id,
                    "timestamp": interaction.timestamp,
                    "type": "buy_signals",
                    "signals": ai_response["buy_signals"]
                })
            
            if ai_response.get("risk_signals") and len(ai_response["risk_signals"]) > 2:
                key_moments.append({
                    "interaction_id": interaction.id,
                    "timestamp": interaction.timestamp,
                    "type": "high_risk",
                    "signals": ai_response["risk_signals"]
                })
        
        # Oblicz trendy
        sentiment_trend = "stable"
        if len(sentiment_timeline) >= 2:
            first_half_avg = sum(s["value"] for s in sentiment_timeline[:len(sentiment_timeline)//2]) / (len(sentiment_timeline)//2)
            second_half_avg = sum(s["value"] for s in sentiment_timeline[len(sentiment_timeline)//2:]) / (len(sentiment_timeline) - len(sentiment_timeline)//2)
            
            if second_half_avg > first_half_avg + 1:
                sentiment_trend = "improving"
            elif second_half_avg < first_half_avg - 1:
                sentiment_trend = "declining"
        
        return {
            "session_id": session_id,
            "total_interactions": len(interactions),
            "duration_minutes": int((interactions[-1].timestamp - interactions[0].timestamp).total_seconds() / 60) if len(interactions) > 1 else 0,
            "sentiment_timeline": sentiment_timeline,
            "potential_timeline": potential_timeline,
            "sentiment_trend": sentiment_trend,
            "key_moments": key_moments,
            "final_sentiment": sentiment_timeline[-1]["value"] if sentiment_timeline else None,
            "final_potential": potential_timeline[-1]["value"] if potential_timeline else None,
            "total_tokens_used": sum(i.tokens_used or 0 for i in interactions),
            "avg_confidence": sum(i.confidence_score or 0 for i in interactions if i.confidence_score) / len([i for i in interactions if i.confidence_score]) if any(i.confidence_score for i in interactions) else None
        }
    
    def _extract_client_profile(self, client: Client) -> Dict[str, Any]:
        """
        Wyciągnij profil klienta do przekazania do AI
        
        Args:
            client: Obiekt klienta z bazy danych
            
        Returns:
            Słownik z profilem klienta
        """
        if not client:
            return {
                "alias": "Nieznany klient",
                "archetype": None,
                "tags": [],
                "notes": None
            }
        
        return {
            "alias": client.alias,
            "archetype": client.archetype,
            "tags": client.tags or [],
            "notes": client.notes,
            "created_at": client.created_at.isoformat() if client.created_at else None,
            "updated_at": client.updated_at.isoformat() if client.updated_at else None
        }
    
    async def _get_session_history(
        self, 
        db: AsyncSession, 
        session_id: int, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Pobierz historię ostatnich interakcji z sesji
        
        Args:
            db: Sesja bazy danych
            session_id: ID sesji
            limit: Maksymalna liczba interakcji
            
        Returns:
            Lista słowników z historią interakcji
        """
        try:
            # Pobierz ostatnie interakcje z sesji
            query = await db.execute(
                select(Interaction)
                .where(Interaction.session_id == session_id)
                .order_by(desc(Interaction.timestamp))
                .limit(limit)
            )
            interactions = query.scalars().all()
            
            # Konwertuj na słowniki w odwrotnej kolejności (najstarsze pierwsze)
            history = []
            for interaction in reversed(interactions):
                history.append({
                    "id": interaction.id,
                    "timestamp": interaction.timestamp.isoformat() if interaction.timestamp else None,
                    "user_input": interaction.user_input,
                    "interaction_type": interaction.interaction_type,
                    "confidence_score": interaction.confidence_score,
                    "archetype_match": interaction.archetype_match,
                    "sentiment_score": interaction.ai_response_json.get("sentiment_score") if interaction.ai_response_json else None,
                    "potential_score": interaction.ai_response_json.get("potential_score") if interaction.ai_response_json else None
                })
            
            return history
            
        except Exception as e:
            logger.error(f"❌ Błąd podczas pobierania historii sesji {session_id}: {e}")
            return []
    
    async def _create_fallback_interaction(
        self,
        db: AsyncSession,
        session_id: int,
        interaction_data: InteractionCreate,
        error_msg: str
    ) -> Interaction:
        """
        Utwórz interakcję fallback gdy AI nie działa
        
        Args:
            db: Sesja bazy danych
            session_id: ID sesji
            interaction_data: Dane interakcji
            error_msg: Komunikat błędu
            
        Returns:
            Utworzona interakcja z fallback response
        """
        logger.warning(f"🔄 Tworzenie fallback interakcji dla sesji {session_id}")
        
        # Użyj starej metody placeholder jako fallback
        session = await db.execute(select(SessionModel).where(SessionModel.id == session_id))
        session = session.scalar_one_or_none()
        
        if not session:
            raise ValueError(f"Sesja o ID {session_id} nie istnieje")
        
        # Przygotuj fallback response
        fallback_response = {
            "main_analysis": f"Analiza automatyczna: '{interaction_data.user_input[:100]}...' - AI niedostępny. Postępuj zgodnie z procedurami sprzedażowymi.",
            "client_archetype": "Nieznany (błąd AI)",
            "confidence_level": 30,
            
            "suggested_actions": [
                {"action": "Zadawaj pytania otwarte", "reasoning": "Zbieraj informacje o potrzebach"},
                {"action": "Słuchaj aktywnie", "reasoning": "Zbuduj zrozumienie sytuacji"},
                {"action": "Przedstaw korzyści produktu", "reasoning": "Buduj wartość oferty"},
                {"action": "Zaproponuj następny krok", "reasoning": "Utrzymaj momentum rozmowy"}
            ],
            
            "buy_signals": ["zainteresowanie", "pytania o szczegóły"],
            "risk_signals": ["wahanie", "brak konkretów"],
            
            "key_insights": [
                "AI niedostępny - polegaj na doświadczeniu",
                "Skup się na potrzebach klienta",
                "Zadawaj pytania kwalifikujące"
            ],
            
            "objection_handlers": {
                "cena": "Pokaż wartość długoterminową i TCO",
                "czas": "Zapytaj o konkretne obawy i harmonogram"
            },
            
            "qualifying_questions": [
                "Co jest najważniejsze w Pana nowym samochodzie?",
                "Jaki jest planowany budżet?",
                "Kiedy chciałby Pan podjąć decyzję?"
            ],
            
            "sentiment_score": 5,
            "potential_score": 5,
            "urgency_level": "medium",
            
            "next_best_action": "Zbierz więcej informacji o potrzebach i sytuacji klienta",
            "follow_up_timing": "W ciągu 24-48 godzin",
            
            # Natychmiastowa odpowiedź (fallback)
            "quick_response": "Rozumiem. Czy mógłby Pan powiedzieć więcej o swoich potrzebach?",
            
            # Metadata błędu
            "is_fallback": True,
            "error_reason": error_msg,
            "processing_time_ms": 0,
            "model_used": "fallback",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Utwórz interakcję z fallback response
        interaction_dict = {
            "session_id": session_id,
            "user_input": interaction_data.user_input,
            "interaction_type": interaction_data.interaction_type,
            "timestamp": datetime.utcnow(),
            "ai_response_json": fallback_response,
            "confidence_score": 30,
            "tokens_used": 0,
            "processing_time_ms": 0,
            "suggested_actions": fallback_response["suggested_actions"],
            "identified_signals": ["AI niedostępny"],
            "archetype_match": "Nieznany (fallback)"
        }
        
        # Zapisz w bazie
        db_interaction = await self.create(db, interaction_dict)
        
        logger.warning(
            f"⚠️ Utworzono fallback interakcję ID: {db_interaction.id} "
            f"dla sesji {session_id} | Reason: {error_msg[:100]}..."
        )
        
        return db_interaction
