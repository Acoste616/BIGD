"""
Schematy Pydantic dla modelu Session
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .client import Client


class SessionBase(BaseModel):
    """
    Bazowy schemat sesji - wspólne pola
    """
    client_id: int = Field(..., description="ID klienta")
    session_type: Optional[str] = Field(None, max_length=50, description="Typ sesji (initial/follow-up/negotiation)")
    summary: Optional[str] = Field(None, description="Podsumowanie sesji")
    key_facts: Optional[Dict[str, Any]] = Field(default={}, description="Kluczowe fakty z rozmowy")
    outcome: Optional[str] = Field(None, max_length=100, description="Wynik sesji")
    sentiment_score: Optional[int] = Field(None, ge=1, le=10, description="Ocena sentymentu")
    potential_score: Optional[int] = Field(None, ge=1, le=10, description="Ocena potencjału sprzedażowego")
    risk_indicators: Optional[Dict[str, Any]] = Field(default={}, description="Wskaźniki ryzyka")


class SessionCreate(SessionBase):
    """
    Schemat do tworzenia nowej sesji - dla bezpośredniego endpointu
    """
    pass


class SessionCreateNested(BaseModel):
    """
    Schemat do tworzenia nowej sesji przez zagnieżdżony endpoint /clients/{id}/sessions/
    client_id jest w URL, więc nie wymagany w body
    """
    session_type: Optional[str] = Field(None, max_length=50, description="Typ sesji (initial/follow-up/negotiation)")
    summary: Optional[str] = Field(None, description="Podsumowanie sesji")
    key_facts: Optional[Dict[str, Any]] = Field(default={}, description="Kluczowe fakty z rozmowy")
    outcome: Optional[str] = Field(None, max_length=100, description="Wynik sesji")
    sentiment_score: Optional[int] = Field(None, ge=1, le=10, description="Ocena sentymentu")
    potential_score: Optional[int] = Field(None, ge=1, le=10, description="Ocena potencjału sprzedażowego")
    risk_indicators: Optional[Dict[str, Any]] = Field(default={}, description="Wskaźniki ryzyka")


class SessionCreateDemo(BaseModel):
    """
    Schemat do tworzenia sesji demo bez klienta
    """
    session_type: Optional[str] = Field("demo", max_length=50, description="Typ sesji (demo)")
    summary: Optional[str] = Field("Demo conversation session", description="Podsumowanie sesji")
    notes: Optional[str] = Field(None, description="Notatki o sesji")  # Dodane dla demo


class SessionDemo(BaseModel):
    """
    Schemat sesji demo - bez wymaganego client_id
    """
    id: int
    client_id: Optional[int] = None  # Opcjonalne dla demo
    start_time: datetime
    end_time: Optional[datetime] = None
    session_type: Optional[str] = None
    summary: Optional[str] = None
    outcome: Optional[str] = None
    sentiment_score: Optional[int] = None
    potential_score: Optional[int] = None
    is_active: bool = Field(default=True, description="Czy sesja jest aktywna")
    duration_minutes: Optional[int] = Field(None, description="Czas trwania sesji w minutach")
    
    model_config = ConfigDict(from_attributes=True)


class SessionUpdate(BaseModel):
    """
    Schemat do aktualizacji sesji
    """
    session_type: Optional[str] = Field(None, max_length=50)
    summary: Optional[str] = None
    key_facts: Optional[Dict[str, Any]] = None
    outcome: Optional[str] = Field(None, max_length=100)
    sentiment_score: Optional[int] = Field(None, ge=1, le=10)
    potential_score: Optional[int] = Field(None, ge=1, le=10)
    risk_indicators: Optional[Dict[str, Any]] = None
    end_time: Optional[datetime] = None


class SessionEnd(BaseModel):
    """
    Schemat do zakończenia sesji
    """
    summary: str = Field(..., description="Podsumowanie sesji")
    outcome: Optional[str] = Field(None, description="Wynik sesji")
    sentiment_score: Optional[int] = Field(None, ge=1, le=10)
    potential_score: Optional[int] = Field(None, ge=1, le=10)


class Session(SessionBase):
    """
    Schemat pełny sesji - zwracany przez API
    """
    id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    is_active: bool = Field(default=True, description="Czy sesja jest aktywna")
    duration_minutes: Optional[int] = Field(None, description="Czas trwania sesji w minutach")
    
    model_config = ConfigDict(from_attributes=True)


class SessionWithClient(Session):
    """
    Schemat sesji z danymi klienta
    """
    
    client: Optional["Client"] = None
    
    model_config = ConfigDict(from_attributes=True)


class SessionWithInteractions(Session):
    """
    Schemat sesji z interakcjami - dla szczegółowego widoku
    """

    
    client: Optional["Client"] = None
    interactions: List["Interaction"] = []
    interactions_count: Optional[int] = None
    total_tokens_used: Optional[int] = None
    avg_confidence_score: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)


class SessionSummary(BaseModel):
    """
    Schemat podsumowania sesji - dla listy
    """
    id: int
    client_id: int
    client_name: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    session_type: Optional[str] = None
    outcome: Optional[str] = None
    sentiment_score: Optional[int] = None
    potential_score: Optional[int] = None
    interactions_count: int = 0
    
    model_config = ConfigDict(from_attributes=True)


class SessionAnalytics(BaseModel):
    """
    Schemat analityki sesji
    """
    session_id: int
    client_archetype: Optional[str] = None
    top_signals: List[str] = []
    risk_factors: List[str] = []
    recommended_actions: List[str] = []
    conversion_probability: Optional[float] = Field(None, ge=0, le=1)
    next_best_action: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# Import cykliczny - rozwiązanie dla typowania
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .client import Client
    from .interaction import Interaction

# Aktualizacja modeli po imporcie
# SessionWithClient.model_rebuild()  # Przeniesione do __init__.py
# SessionWithInteractions.model_rebuild()  # Przeniesione do __init__.py
