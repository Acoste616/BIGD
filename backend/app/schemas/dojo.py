"""
AI Dojo Schemas - Schematy Pydantic dla modułu treningowego AI

Moduł 3: Interaktywne AI Dojo "Sparing z Mistrzem"
Cel: Umożliwienie ekspertom błyskawiczne uczenie AI nowych informacji
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime


class DojoMessageRequest(BaseModel):
    """
    Schemat żądania wiadomości w AI Dojo
    
    Przesyłane przez administratora/eksperta do AI w celu:
    - Przekazania nowej wiedzy do nauki
    - Pytania o określony temat  
    - Korekty błędnych informacji AI
    """
    message: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Wiadomość od eksperta do AI (nowa wiedza, pytanie, korekta)"
    )
    
    conversation_history: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Historia konwersacji treningowej (dla kontekstu)"
    )
    
    training_mode: Optional[Literal["knowledge_update", "error_correction", "general_chat"]] = Field(
        default="knowledge_update",
        description="Tryb treningu: aktualizacja wiedzy, korekta błędów, lub ogólna rozmowa"
    )
    
    client_context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Opcjonalny kontekst klienta (jeśli trening dotyczy konkretnego przypadku)"
    )


class DojoMessageResponse(BaseModel):
    """
    Schemat odpowiedzi AI Dojo
    
    AI może odpowiedzieć w różny sposób:
    - Zadać pytania doprecyzowujące (response_type="question")
    - Przygotować dane do zapisu (response_type="confirmation") 
    - Potwierdzić zrozumienie (response_type="status")
    """
    response: str = Field(
        ...,
        description="Odpowiedź tekstowa AI (pytanie, potwierdzenie, status)"
    )
    
    response_type: Literal["question", "confirmation", "status", "error"] = Field(
        ...,
        description="Typ odpowiedzi: pytanie, potwierdzenie zapisu, status, lub błąd"
    )
    
    structured_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Ustrukturyzowane dane gotowe do zapisu w Qdrant (tylko dla type='confirmation')"
    )
    
    confidence_level: Optional[int] = Field(
        default=None,
        ge=0, le=100,
        description="Poziom pewności AI co do zrozumienia (0-100%)"
    )
    
    suggested_follow_up: Optional[List[str]] = Field(
        default=None,
        description="Sugerowane pytania kontynuacyjne"
    )
    
    processing_time_ms: Optional[int] = Field(
        default=None,
        description="Czas przetwarzania w milisekundach"
    )
    
    timestamp: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="Timestamp odpowiedzi"
    )


class KnowledgeFormatRequest(BaseModel):
    """
    Schemat żądania formatowania wiedzy do zapisu w Qdrant
    
    Używane gdy AI przygotowuje dane do strukturalnego zapisu
    """
    raw_content: str = Field(
        ...,
        description="Surowa treść do sformatowania"
    )
    
    knowledge_type: Optional[str] = Field(
        default="general",
        description="Typ wiedzy (general, objection, closing, product, etc.)"
    )
    
    target_archetype: Optional[str] = Field(
        default=None,
        description="Docelowy archetyp klienta (jeśli wiedza jest specyficzna)"
    )
    
    context_tags: Optional[List[str]] = Field(
        default_factory=list,
        description="Tagi kontekstowe dla lepszego wyszukiwania"
    )


class DojoSessionSummary(BaseModel):
    """
    Schemat podsumowania sesji treningowej
    
    Przechowuje kompletne podsumowanie sesji AI Dojo
    """
    session_id: str = Field(
        ...,
        description="Unikalny identyfikator sesji treningowej"
    )
    
    expert_name: Optional[str] = Field(
        default="Administrator",
        description="Nazwa eksperta prowadzącego trening"
    )
    
    total_messages: int = Field(
        ...,
        ge=0,
        description="Łączna liczba wiadomości w sesji"
    )
    
    knowledge_items_added: int = Field(
        default=0,
        ge=0,
        description="Liczba dodanych elementów wiedzy"
    )
    
    corrections_made: int = Field(
        default=0,
        ge=0,
        description="Liczba wykonanych korekt"
    )
    
    session_duration_minutes: Optional[int] = Field(
        default=None,
        ge=0,
        description="Czas trwania sesji w minutach"
    )
    
    topics_covered: List[str] = Field(
        default_factory=list,
        description="Lista tematów poruszonych w sesji"
    )
    
    ai_confidence_improvement: Optional[float] = Field(
        default=None,
        ge=0.0, le=100.0,
        description="Poprawa pewności AI w % (przed/po sesji)"
    )
    
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Data rozpoczęcia sesji"
    )
    
    completed_at: Optional[datetime] = Field(
        default=None,
        description="Data zakończenia sesji"
    )


class DojoAnalyticsResponse(BaseModel):
    """
    Schemat odpowiedzi analityki AI Dojo
    
    Statystyki wykorzystania i skuteczności treningu
    """
    total_training_sessions: int = Field(
        ...,
        ge=0,
        description="Łączna liczba sesji treningowych"
    )
    
    knowledge_items_total: int = Field(
        ...,
        ge=0,
        description="Łączna liczba elementów wiedzy dodanych przez Dojo"
    )
    
    avg_session_duration: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Średni czas trwania sesji treningowej (minuty)"
    )
    
    most_active_experts: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Lista najaktywniejszych ekspertów"
    )
    
    popular_topics: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Najpopularniejsze tematy treningowe"
    )
    
    ai_improvement_trend: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Trend poprawy AI w czasie"
    )
    
    last_updated: datetime = Field(
        default_factory=datetime.now,
        description="Data ostatniej aktualizacji statystyk"
    )


# Pomocnicze typy dla lepszego type hinting
DojoConversationHistory = List[Dict[str, Any]]
StructuredKnowledge = Dict[str, Any]
TrainingMetrics = Dict[str, float]

# Eksporty dla łatwego importowania
__all__ = [
    "DojoMessageRequest",
    "DojoMessageResponse", 
    "KnowledgeFormatRequest",
    "DojoSessionSummary",
    "DojoAnalyticsResponse",
    "DojoConversationHistory",
    "StructuredKnowledge",
    "TrainingMetrics"
]
