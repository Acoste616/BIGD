"""
Schematy Pydantic dla modelu Interaction
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .feedback import Feedback
    from .session import Session
    from .client import Client


class InteractionBase(BaseModel):
    """
    Bazowy schemat interakcji - wspólne pola
    """
    session_id: int = Field(..., description="ID sesji")
    user_input: str = Field(..., min_length=1, description="Wejście od użytkownika")
    interaction_type: Optional[str] = Field(None, max_length=50, description="Typ interakcji (observation/question/objection)")


class InteractionCreate(InteractionBase):
    """
    Schemat do tworzenia nowej interakcji - dla bezpośredniego endpointu
    """
    pass


class InteractionCreateNested(BaseModel):
    """
    Schemat do tworzenia nowej interakcji przez zagnieżdżony endpoint /sessions/{id}/interactions/
    session_id jest w URL, więc nie wymagany w body
    """
    user_input: str = Field(..., min_length=1, description="Wejście od użytkownika")
    interaction_type: Optional[str] = Field(None, max_length=50, description="Typ interakcji (observation/question/objection)")


class InteractionUpdate(BaseModel):
    """
    Schemat do aktualizacji interakcji (głównie dla dodania feedback)
    """
    interaction_type: Optional[str] = Field(None, max_length=50)
    confidence_score: Optional[int] = Field(None, ge=0, le=100)


class Interaction(InteractionBase):
    """
    Schemat pełny interakcji - zwracany przez API
    """
    id: int
    timestamp: datetime
    ai_response_json: Dict[str, Any] = Field(..., description="Pełna odpowiedź AI")
    confidence_score: Optional[int] = Field(None, ge=0, le=100, description="Pewność AI (0-100)")
    tokens_used: Optional[int] = Field(None, description="Liczba zużytych tokenów")
    processing_time_ms: Optional[int] = Field(None, description="Czas przetwarzania w ms")
    suggested_actions: Optional[List[Dict[str, Any]]] = Field(default=[], description="Sugerowane akcje")
    identified_signals: Optional[List[str]] = Field(default=[], description="Zidentyfikowane sygnały")
    archetype_match: Optional[str] = Field(None, description="Dopasowany archetyp")
    
    model_config = ConfigDict(from_attributes=True)


class InteractionWithFeedback(Interaction):
    """
    Schemat interakcji z feedbackiem
    """

    
    feedbacks: List["Feedback"] = []
    feedback_score: Optional[float] = Field(None, description="Średnia ocena feedbacku")
    
    model_config = ConfigDict(from_attributes=True)


class InteractionWithContext(Interaction):
    """
    Schemat interakcji z kontekstem sesji i klienta
    """

    
    session: Optional["Session"] = None
    client: Optional["Client"] = None
    feedbacks: List["Feedback"] = []
    
    model_config = ConfigDict(from_attributes=True)


class ArchetypeMatch(BaseModel):
    """
    Schemat pojedynczego dopasowania archetypu
    """
    name: str = Field(..., description="Nazwa archetypu")
    confidence: int = Field(..., ge=0, le=100, description="Pewność dopasowania (0-100)")
    description: Optional[str] = Field(None, description="Krótki opis archetypu")


class InteractionResponse(BaseModel):
    """
    Schemat odpowiedzi AI - struktura zwracana przez model
    Uwzględnia nowe zasady generowania odpowiedzi (holistyczne vs atomowe)
    """
    # Natychmiastowa odpowiedź (HOLISTYCZNA - na podstawie całej historii)
    quick_response: str = Field(
        ...,
        max_length=300,
        description="Krótka, naturalna odpowiedź spójna z CAŁĄ historią rozmowy - gotowa do natychmiastowego użycia"
    )
    
    # Pytania pogłębiające (ATOMOWE - tylko dla ostatniej wypowiedzi)
    suggested_questions: List[str] = Field(
        default=[],
        description="Pytania pogłębiające dotyczące TYLKO ostatniej wypowiedzi klienta",
        max_length=5
    )
    
    # Analiza holistyczna
    main_analysis: str = Field(..., description="Holistyczna analiza całej sytuacji na podstawie pełnej historii")
    client_archetype: str = Field(..., description="Zidentyfikowany archetyp na podstawie całokształtu interakcji")
    confidence_level: int = Field(..., ge=0, le=100, description="Poziom pewności analizy")
    
    # Archetypy z prawdopodobieństwami (dla panelu strategicznego)
    likely_archetypes: List[ArchetypeMatch] = Field(
        default=[],
        description="1-2 najbardziej prawdopodobne archetypy z procentowym dopasowaniem",
        max_length=2
    )
    
    # Insights strategiczne (dla panelu strategicznego)
    strategic_notes: List[str] = Field(
        default=[],
        description="Kluczowe insights strategiczne dla panelu strategicznego",
        max_length=5
    )
    
    # Sugerowane akcje (bez ograniczenia do 4)
    suggested_actions: List[Dict[str, str]] = Field(
        default=[],
        description="Lista sugerowanych akcji z uzasadnieniem",
        max_length=6
    )
    
    # Analiza sygnałów
    buy_signals: List[str] = Field(default=[], description="Sygnały kupna")
    risk_signals: List[str] = Field(default=[], description="Sygnały ryzyka")
    
    # Obsługa zastrzeżeń
    objection_handlers: Dict[str, str] = Field(default={}, description="Obsługa zastrzeżeń")
    
    # Oceny
    sentiment_score: int = Field(..., ge=1, le=10, description="Ocena sentymentu")
    potential_score: int = Field(..., ge=1, le=10, description="Ocena potencjału")
    urgency_level: str = Field(..., description="Poziom pilności (low/medium/high)")
    
    # Następne kroki
    next_best_action: str = Field(..., description="Najważniejsza następna akcja wynikająca z całokształtu analizy")
    follow_up_timing: Optional[str] = Field(None, description="Rekomendowany timing następnego kontaktu")
    
    model_config = ConfigDict(from_attributes=True)


class InteractionRequest(BaseModel):
    """
    Schemat żądania analizy - wysyłany do AI
    """
    session_id: int
    user_input: str
    context: Dict[str, Any] = Field(default={}, description="Kontekst rozmowy")
    client_history: Optional[List[Dict[str, Any]]] = Field(default=[], description="Historia klienta")
    session_history: Optional[List[Dict[str, Any]]] = Field(default=[], description="Historia sesji")
    max_tokens: Optional[int] = Field(None, description="Limit tokenów odpowiedzi")
    
    model_config = ConfigDict(from_attributes=True)


# Import cykliczny - rozwiązanie dla typowania
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .feedback import Feedback
    from .session import Session
    from .client import Client

# Aktualizacja modeli po imporcie
# InteractionWithFeedback.model_rebuild()  # Przeniesione do __init__.py
# InteractionWithContext.model_rebuild()  # Przeniesione do __init__.py
