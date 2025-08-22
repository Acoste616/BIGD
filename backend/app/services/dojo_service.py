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
