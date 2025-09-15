"""
AI Dojo Service - Serwis treningowy dla Modułu 3

Moduł 3: Interaktywne AI Dojo "Sparing z Mistrzem"
Cel: Umożliwienie ekspertom błyskawiczne uczenie AI i aktualizowanie bazy wiedzy

ARCHITEKTURA:
- handle_dojo_conversation(): Główna funkcja zarządzania konwersacją treningową
- Integracja z ai_service.py (mode='training')
- Integracja z qdrant_service.py (zapis strukturalnej wiedzy)
- Stan konwersacji zarządzany przez frontend
"""
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from app.schemas.dojo import (
    DojoMessageRequest, 
    DojoMessageResponse,
    StructuredKnowledge
)
from app.services.ai_service import ai_service
from app.services.qdrant_service import qdrant_service
from app.repositories.interaction_repository import InteractionRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.client_repository import ClientRepository
from app.repositories.feedback_repository import FeedbackRepository
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

logger = logging.getLogger(__name__)


class AdminDialogueService:
    """
    Serwis zarządzania dialogiem treningowym między ekspertem a AI
    
    Funkcjonalności:
    - Zarządzanie konwersacją treningową
    - Integracja z AI Service (tryb training)
    - Zapis strukturalnej wiedzy do Qdrant
    - Zarządzanie stanami treningu (3 poziomy inteligencji)
    """
    
    def __init__(self):
        """
        Inicjalizacja serwisu z integracją AI i Qdrant
        """
        self.ai_service = ai_service
        self.qdrant_service = qdrant_service
        
        # Słownik aktywnych sesji treningowych (w pamięci)
        # W produkcji można to przenieść do Redis/DB
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
        logger.info("✅ AI Dojo Service zainicjalizowany z integracją AI + Qdrant")
    
    async def handle_dojo_conversation(
        self,
        request: DojoMessageRequest,
        session_id: Optional[str] = None,
        expert_name: str = "Administrator"
    ) -> DojoMessageResponse:
        """
        GŁÓWNA FUNKCJA: Obsługa konwersacji treningowej w AI Dojo
        
        Przepływ:
        1. Zarządza stanem sesji treningowej
        2. Wywołuje AI Service w trybie 'training'
        3. Analizuje odpowiedź AI
        4. Jeśli AI przygotował structured_data → obsługa zapisu do Qdrant
        5. Zwraca odpowiedź do frontend
        
        Args:
            request: DojoMessageRequest z wiadomością eksperta
            session_id: ID sesji treningowej (opcjonalne, auto-generowane)
            expert_name: Nazwa eksperta (dla metadanych)
            
        Returns:
            DojoMessageResponse z odpowiedzią AI lub statusem operacji
        """
        start_time = datetime.now()
        
        try:
            # 1. ZARZĄDZANIE SESJĄ TRENINGOWĄ
            if not session_id:
                session_id = self._generate_session_id()
                logger.info(f"🎓 AI Dojo: Rozpoczynam nową sesję treningową: {session_id}")
            
            # Pobierz/utwórz sesję treningową
            training_session = self._get_or_create_session(session_id, expert_name)
            
            # Dodaj wiadomość eksperta do historii
            training_session["messages"].append({
                "timestamp": datetime.now().isoformat(),
                "sender": "expert",
                "message": request.message,
                "training_mode": request.training_mode
            })
            
            logger.info(f"🎓 AI Dojo [{session_id}]: Przetwarzam wiadomość eksperta ({len(request.message)} znaków)")
            
            # 2. WYWOŁANIE AI SERVICE W TRYBIE TRENINGOWYM
            
            # Przygotuj kontekst dla AI
            session_context = {
                "session_id": session_id,
                "training_mode": request.training_mode,
                "expert_name": expert_name,
                "total_messages": len(training_session["messages"])
            }
            
            # Historia konwersacji treningowej (ostatnie 10 wiadomości)
            conversation_history = training_session["messages"][-10:]
            
            # Wywołaj AI Service z mode='training'
            ai_response = await self.ai_service.generate_analysis(
                user_input=request.message,
                client_profile=request.client_context or {},  # Opcjonalny kontekst klienta
                session_history=conversation_history,
                session_context=session_context,
                mode='training'  # KLUCZOWE: Tryb treningowy
            )
            
            logger.info(f"✅ AI Dojo: Otrzymano odpowiedź AI typu '{ai_response.get('response_type')}'")
            
            # 3. ANALIZA I PRZETWARZANIE ODPOWIEDZI AI
            
            # Dodaj odpowiedź AI do historii sesji
            training_session["messages"].append({
                "timestamp": datetime.now().isoformat(),
                "sender": "ai",
                "response": ai_response.get("response"),
                "response_type": ai_response.get("response_type"),
                "confidence_level": ai_response.get("confidence_level", 70)
            })
            
            # 4. OBSŁUGA ZAPISU WIEDZY (jeśli AI przygotował structured_data)
            
            dojo_response = None
            
            if ai_response.get("response_type") == "confirmation" and ai_response.get("structured_data"):
                # AI przygotował dane do zapisu - czeka na potwierdzenie eksperta
                logger.info("📋 AI Dojo: AI przygotował strukturalne dane do zapisu")
                
                dojo_response = DojoMessageResponse(
                    response=ai_response.get("response", "Przygotowałem dane do zapisu. Czy zatwierdzić?"),
                    response_type="confirmation",
                    structured_data=ai_response.get("structured_data"),
                    confidence_level=ai_response.get("confidence_level", 85),
                    suggested_follow_up=["Zatwierdź i zapisz", "Anuluj", "Modyfikuj dane"],
                    processing_time_ms=ai_response.get("processing_time_ms", 0)
                )
                
            elif ai_response.get("response_type") == "question":
                # AI zadaje pytania doprecyzowujące
                logger.info("❓ AI Dojo: AI zadaje pytania doprecyzowujące")
                
                dojo_response = DojoMessageResponse(
                    response=ai_response.get("response", "Potrzebuję więcej informacji."),
                    response_type="question",
                    confidence_level=ai_response.get("confidence_level", 60),
                    suggested_follow_up=ai_response.get("suggested_follow_up", []),
                    processing_time_ms=ai_response.get("processing_time_ms", 0)
                )
                
            else:
                # AI podaje status/błąd/inne
                logger.info(f"ℹ️ AI Dojo: AI odpowiada statusem ({ai_response.get('response_type')})")
                
                dojo_response = DojoMessageResponse(
                    response=ai_response.get("response", "Rozumiem."),
                    response_type=ai_response.get("response_type", "status"),
                    confidence_level=ai_response.get("confidence_level", 70),
                    processing_time_ms=ai_response.get("processing_time_ms", 0)
                )
            
            # 5. AKTUALIZACJA METADANYCH SESJI
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            training_session["last_activity"] = datetime.now().isoformat()
            training_session["total_processing_time_ms"] += int(processing_time)
            
            # Zapisz sesję w pamięci
            self.active_sessions[session_id] = training_session
            
            logger.info(f"⚡ AI Dojo: Konwersacja przetworzona w {processing_time:.0f}ms")
            
            return dojo_response
            
        except Exception as e:
            logger.error(f"❌ AI Dojo: Błąd podczas obsługi konwersacji: {e}")
            
            # Fallback response
            return DojoMessageResponse(
                response=f"Przepraszam, wystąpił błąd podczas przetwarzania: {str(e)[:200]}",
                response_type="error",
                confidence_level=0,
                suggested_follow_up=["Spróbuj ponownie", "Przeformułuj wiadomość"],
                processing_time_ms=0
            )
    
    async def confirm_knowledge_write(
        self,
        session_id: str,
        structured_data: StructuredKnowledge,
        expert_confirmation: bool = True
    ) -> DojoMessageResponse:
        """
        Potwierdź i zapisz strukturalną wiedzę do bazy Qdrant
        
        Wywoływane gdy ekspert zatwierdza dane przygotowane przez AI
        
        Args:
            session_id: ID sesji treningowej
            structured_data: Ustrukturyzowane dane do zapisu
            expert_confirmation: Czy ekspert zatwierdził zapis
            
        Returns:
            DojoMessageResponse z statusem operacji
        """
        try:
            if not expert_confirmation:
                logger.info(f"🚫 AI Dojo [{session_id}]: Ekspert anulował zapis wiedzy")
                return DojoMessageResponse(
                    response="Operacja anulowana przez eksperta.",
                    response_type="status",
                    confidence_level=100
                )
            
            logger.info(f"💾 AI Dojo [{session_id}]: Zapisuję strukturalną wiedzę do Qdrant")
            
            # Przygotuj dane do zapisu w Qdrant (format zgodny z qdrant_service)
            knowledge_point = {
                "title": structured_data.get("title", "Wiedza z AI Dojo"),
                "content": structured_data.get("content", ""),
                "knowledge_type": structured_data.get("knowledge_type", "general"),
                "archetype": structured_data.get("archetype"),  # Może być None dla ogólnych
                "tags": structured_data.get("tags", []),
                "source": structured_data.get("source", "AI Dojo"),
                "created_at": datetime.now().isoformat(),
                "session_id": session_id
            }
            
            # Zapisz do Qdrant (używamy istniejącego serwisu)
            point_id = await self._save_knowledge_to_qdrant(knowledge_point)
            
            # Aktualizuj statystyki sesji
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                session["knowledge_items_added"] += 1
                session["last_knowledge_write"] = datetime.now().isoformat()
                
                # Dodaj do historii
                session["messages"].append({
                    "timestamp": datetime.now().isoformat(),
                    "sender": "system",
                    "message": f"✅ Wiedza zapisana w bazie (ID: {point_id})",
                    "knowledge_point_id": point_id
                })
            
            logger.info(f"✅ AI Dojo: Wiedza zapisana pomyślnie (ID: {point_id})")
            
            return DojoMessageResponse(
                response=f"✅ Wiedza została pomyślnie zapisana w bazie danych (ID: {point_id}). Możesz kontynuować trening lub dodać kolejne informacje.",
                response_type="status", 
                confidence_level=100,
                structured_data={"saved_point_id": point_id, "status": "saved"}
            )
            
        except Exception as e:
            logger.error(f"❌ AI Dojo: Błąd podczas zapisu wiedzy: {e}")
            
            return DojoMessageResponse(
                response=f"❌ Błąd podczas zapisywania wiedzy: {str(e)[:200]}. Spróbuj ponownie.",
                response_type="error",
                confidence_level=0,
                suggested_follow_up=["Spróbuj ponownie", "Sprawdź dane"]
            )
    
    async def _save_knowledge_to_qdrant(self, knowledge_point: Dict[str, Any]) -> str:
        """
        Zapisz punkt wiedzy do Qdrant (używa istniejący qdrant_service)
        
        Args:
            knowledge_point: Strukturalne dane wiedzy
            
        Returns:
            ID zapisanego punktu w Qdrant
        """
        try:
            # Wywołaj istniejący serwis Qdrant (nie modyfikujemy go)
            # UWAGA: archetype może być None - qdrant_service.py obsługuje to poprawnie
            archetype_value = knowledge_point.get("archetype")
            if archetype_value is not None and not isinstance(archetype_value, str):
                archetype_value = str(archetype_value)
                
            point_id = self.qdrant_service.add_knowledge(
                content=knowledge_point["content"],
                title=knowledge_point["title"],
                knowledge_type=knowledge_point["knowledge_type"],
                archetype=archetype_value,  # type: ignore  # qdrant_service obsługuje None
                tags=knowledge_point.get("tags", []),
                source=knowledge_point.get("source", "AI Dojo")
            )
            
            return point_id
            
        except Exception as e:
            logger.error(f"❌ Błąd podczas zapisu do Qdrant: {e}")
            raise
    
    def _generate_session_id(self) -> str:
        """
        Wygeneruj unikalny ID sesji treningowej
        """
        return f"dojo_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}"
    
    def _get_or_create_session(self, session_id: str, expert_name: str) -> Dict[str, Any]:
        """
        Pobierz istniejącą sesję treningową lub utwórz nową
        
        Args:
            session_id: ID sesji
            expert_name: Nazwa eksperta
            
        Returns:
            Słownik z danymi sesji treningowej
        """
        if session_id not in self.active_sessions:
            # Utwórz nową sesję treningową
            self.active_sessions[session_id] = {
                "session_id": session_id,
                "expert_name": expert_name,
                "created_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "messages": [],
                "knowledge_items_added": 0,
                "total_processing_time_ms": 0,
                "last_knowledge_write": None,
                "status": "active"
            }
            logger.info(f"🆕 AI Dojo: Utworzono nową sesję treningową: {session_id}")
        else:
            logger.debug(f"📂 AI Dojo: Kontynuuję istniejącą sesję: {session_id}")
        
        return self.active_sessions[session_id]
    
    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Pobierz podsumowanie sesji treningowej
        
        Args:
            session_id: ID sesji
            
        Returns:
            Słownik z podsumowaniem lub None jeśli sesja nie istnieje
        """
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        
        # Oblicz statystyki
        total_messages = len(session["messages"])
        expert_messages = len([m for m in session["messages"] if m.get("sender") == "expert"])
        ai_messages = len([m for m in session["messages"] if m.get("sender") == "ai"])
        
        created_at = datetime.fromisoformat(session["created_at"])
        duration_minutes = (datetime.now() - created_at).total_seconds() / 60
        
        return {
            "session_id": session_id,
            "expert_name": session["expert_name"],
            "status": session["status"],
            "duration_minutes": int(duration_minutes),
            "total_messages": total_messages,
            "expert_messages": expert_messages,
            "ai_messages": ai_messages,
            "knowledge_items_added": session["knowledge_items_added"],
            "avg_processing_time_ms": session["total_processing_time_ms"] // max(ai_messages, 1),
            "created_at": session["created_at"],
            "last_activity": session["last_activity"]
        }
    
    def get_active_sessions_count(self) -> int:
        """
        Pobierz liczbę aktywnych sesji treningowych
        """
        return len([s for s in self.active_sessions.values() if s["status"] == "active"])
    
    def close_session(self, session_id: str) -> bool:
        """
        Zamknij sesję treningową
        
        Args:
            session_id: ID sesji do zamknięcia
            
        Returns:
            True jeśli sesja została zamknięta, False jeśli nie istniała
        """
        if session_id not in self.active_sessions:
            return False
        
        self.active_sessions[session_id]["status"] = "closed"
        self.active_sessions[session_id]["closed_at"] = datetime.now().isoformat()
        
        logger.info(f"🔚 AI Dojo: Zamknięto sesję treningową: {session_id}")
        return True

    async def process_feedback_for_learning(
        self,
        feedback_id: int,
        interaction_id: int,
        suggestion_id: str,
        suggestion_type: str,
        rating: int
    ) -> bool:
        """
        Process feedback for learning by creating knowledge nuggets
        
        Args:
            feedback_id: ID of the feedback record
            interaction_id: ID of the interaction
            suggestion_id: ID of the suggestion being rated
            suggestion_type: Type of suggestion (quick_response, suggested_action)
            rating: Rating value (1 for positive, -1 for negative)

        Returns:
            bool: True if processing was successful
        """
        # Initialize repositories
        interaction_repo = InteractionRepository()
        session_repo = SessionRepository()
        client_repo = ClientRepository()
        feedback_repo = FeedbackRepository()
        
        try:
            # Create a new database session for this operation
            from app.core.database import AsyncSessionLocal
            async with AsyncSessionLocal() as db:
                # 1. Retrieve interaction and session data
                interaction = await interaction_repo.get_interaction(db, interaction_id)
                if not interaction:
                    logger.error(f"Interaction {interaction_id} not found")
                    return False
                
                session = await session_repo.get_session(db, interaction.session_id)
                if not session:
                    logger.error(f"Session {interaction.session_id} not found")
                    return False
                    
                client = await client_repo.get_client(db, session.client_id)
                if not client:
                    logger.error(f"Client {session.client_id} not found")
                    return False
                
                # 2. Extract suggestion content from AI response
                suggestion_content = self._extract_suggestion_content(
                    interaction.ai_response_json,
                    suggestion_id,
                    suggestion_type
                )
                
                if not suggestion_content:
                    logger.warning(f"Suggestion {suggestion_id} of type {suggestion_type} not found in interaction {interaction_id}")
                    # Try to get more details about the AI response structure
                    ai_response_keys = list(interaction.ai_response_json.keys()) if isinstance(interaction.ai_response_json, dict) else "Not a dict"
                    logger.debug(f"AI response keys: {ai_response_keys}")
                    return False
                
                # 3. Create knowledge nugget
                knowledge_nugget = self._create_knowledge_nugget(
                    client=client,
                    suggestion_content=suggestion_content,
                    suggestion_type=suggestion_type,
                    rating=rating
                )
                
                # Log the knowledge nugget being created
                logger.info(f"Creating knowledge nugget: {knowledge_nugget['title']}")
                logger.debug(f"Knowledge nugget content: {knowledge_nugget['content']}")
                
                # 4. Store in Qdrant
                try:
                    point_id = await self.qdrant_service.add_knowledge(
                        content=knowledge_nugget["content"],
                        title=knowledge_nugget["title"],
                        knowledge_type=knowledge_nugget["knowledge_type"],
                        archetype=knowledge_nugget["archetype"],
                        tags=knowledge_nugget["tags"],
                        source=knowledge_nugget["source"]
                    )
                    logger.info(f"Successfully stored knowledge nugget in Qdrant with point ID: {point_id}")
                except Exception as qdrant_error:
                    logger.error(f"Failed to store knowledge nugget in Qdrant: {qdrant_error}")
                    raise
                
                # 5. Mark feedback as processed
                mark_result = await feedback_repo.mark_feedback_as_processed(db, feedback_id)
                if not mark_result:
                    logger.warning(f"Failed to mark feedback {feedback_id} as processed")
                else:
                    logger.info(f"Successfully marked feedback {feedback_id} as processed")
                
            logger.info(f"Successfully processed feedback for learning: {suggestion_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing feedback for learning - feedback_id: {feedback_id}, interaction_id: {interaction_id}, suggestion_id: {suggestion_id}, error: {e}")
            return False

    def _extract_suggestion_content(
        self,
        ai_response: Dict[str, Any],
        suggestion_id: str,
        suggestion_type: str
    ) -> Optional[str]:
        """
        Extract suggestion content from AI response based on ID and type
        """
        if not ai_response or not isinstance(ai_response, dict):
            return None
            
        try:
            if suggestion_type == "quick_response":
                # Handle direct quick_response structure
                if ai_response.get("quick_response", {}).get("id") == suggestion_id:
                    return ai_response["quick_response"]["text"]
                # Handle nested quick_response structure
                quick_response = ai_response.get("quick_response", {})
                if isinstance(quick_response, dict) and quick_response.get("id") == suggestion_id:
                    return quick_response.get("text") or quick_response.get("content")
                    
            elif suggestion_type == "suggested_action":
                # Handle array of suggested_actions
                suggested_actions = ai_response.get("suggested_actions", [])
                if isinstance(suggested_actions, list):
                    for action in suggested_actions:
                        if isinstance(action, dict) and action.get("id") == suggestion_id:
                            return action.get("text") or action.get("action") or action.get("content")
                
                # Handle single suggested_action
                single_action = ai_response.get("suggested_action", {})
                if isinstance(single_action, dict) and single_action.get("id") == suggestion_id:
                    return single_action.get("text") or single_action.get("action") or single_action.get("content")
                    
            # Generic fallback for any suggestion type
            # Check if there's a suggestions array or dict
            suggestions = ai_response.get("suggestions", {})
            if isinstance(suggestions, dict):
                suggestion = suggestions.get(suggestion_id)
                if isinstance(suggestion, dict):
                    return suggestion.get("text") or suggestion.get("content") or suggestion.get("action")
                elif isinstance(suggestion, str):
                    return suggestion
                    
            # Check if ai_response itself contains the suggestion_id
            if ai_response.get(suggestion_id):
                suggestion = ai_response.get(suggestion_id)
                if isinstance(suggestion, dict):
                    return suggestion.get("text") or suggestion.get("content") or suggestion.get("action")
                elif isinstance(suggestion, str):
                    return suggestion
                    
        except Exception as e:
            logger.error(f"Error extracting suggestion content: {e}")
            
        return None

    def _create_knowledge_nugget(
        self,
        client: Any,
        suggestion_content: str,
        suggestion_type: str,
        rating: int
    ) -> Dict[str, Any]:
        """
        Create a knowledge nugget from feedback data
        """
        client_archetype = getattr(client, "archetype", "Unknown") if client else "Unknown"
        
        if rating > 0:  # Positive feedback
            title = f"Effective {suggestion_type} for {client_archetype} archetype"
            content = f"For client with archetype '{client_archetype}', suggestion '{suggestion_content}' was effective."
        else:  # Negative feedback
            title = f"Ineffective {suggestion_type} for {client_archetype} archetype"
            content = f"For client with archetype '{client_archetype}', suggestion '{suggestion_content}' was ineffective."
        
        return {
            "title": title,
            "content": content,
            "knowledge_type": "feedback_learning",
            "archetype": client_archetype,
            "tags": ["feedback", "learning", suggestion_type],
            "source": "user_feedback"
        }

# Singleton instancja serwisu AI Dojo
admin_dialogue_service = AdminDialogueService()


# Główna funkcja eksportowa (zgodnie z planem)
async def handle_dojo_conversation(
    request: DojoMessageRequest,
    session_id: Optional[str] = None,
    expert_name: str = "Administrator"
) -> DojoMessageResponse:
    """
    Główna funkcja obsługi konwersacji AI Dojo - eksportowa funkcja modułu
    
    Args:
        request: DojoMessageRequest z wiadomością eksperta
        session_id: Opcjonalny ID sesji treningowej
        expert_name: Nazwa eksperta prowadzącego trening
        
    Returns:
        DojoMessageResponse z odpowiedzią AI lub statusem operacji
    """
    return await admin_dialogue_service.handle_dojo_conversation(
        request=request,
        session_id=session_id,
        expert_name=expert_name
    )


# Funkcja potwierdzania zapisu wiedzy
async def confirm_knowledge_write(
    session_id: str,
    structured_data: StructuredKnowledge,
    expert_confirmation: bool = True
) -> DojoMessageResponse:
    """
    Potwierdź i zapisz strukturalną wiedzę do bazy Qdrant
    
    Args:
        session_id: ID sesji treningowej
        structured_data: Ustrukturyzowane dane do zapisu
        expert_confirmation: Czy ekspert zatwierdził zapis
        
    Returns:
        DojoMessageResponse z statusem operacji
    """
    return await admin_dialogue_service.confirm_knowledge_write(
        session_id=session_id,
        structured_data=structured_data,
        expert_confirmation=expert_confirmation
    )


# Eksport wszystkich kluczowych funkcji
__all__ = [
    "AdminDialogueService",
    "admin_dialogue_service",
    "handle_dojo_conversation",
    "confirm_knowledge_write"
]
