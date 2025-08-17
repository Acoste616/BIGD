"""
Schematy Pydantic dla modelu Client
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .session import Session


class ClientBase(BaseModel):
    """
    Bazowy schemat klienta - tylko dane profilujące (pełna anonimizacja)
    """
    alias: str = Field(..., min_length=1, max_length=50, description="Alias klienta (auto-generowany)")
    notes: Optional[str] = Field(None, description="Notatki analityczne o kliencie")
    archetype: Optional[str] = Field(None, max_length=100, description="Archetyp klienta")
    tags: Optional[List[str]] = Field(default=[], description="Lista tagów/etykiet profilujących")


class ClientCreate(BaseModel):
    """
    Schemat do tworzenia nowego klienta (tylko dane profilujące)
    """
    notes: Optional[str] = Field(None, description="Notatki analityczne o kliencie")
    archetype: Optional[str] = Field(None, max_length=100, description="Archetyp klienta")
    tags: Optional[List[str]] = Field(default=[], description="Lista tagów/etykiet profilujących")


class ClientUpdate(BaseModel):
    """
    Schemat do aktualizacji klienta - tylko dane profilujące (alias nie można zmieniać)
    """
    notes: Optional[str] = None
    archetype: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None


class Client(ClientBase):
    """
    Schemat pełny klienta - zwracany przez API
    """
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Konfiguracja dla Pydantic V2
    model_config = ConfigDict(from_attributes=True)


class ClientWithSessions(Client):
    """
    Schemat klienta z sesjami - dla szczegółowego widoku
    """
    
    sessions: List["Session"] = []
    sessions_count: Optional[int] = None
    last_session_date: Optional[datetime] = None
    total_interactions: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class ClientSummary(BaseModel):
    """
    Schemat podsumowania klienta - tylko dane profilujące (pełna anonimizacja)
    """
    id: int
    alias: str
    archetype: Optional[str] = None
    tags: List[str] = []
    sessions_count: int = 0
    last_contact: Optional[datetime] = None
    potential_score: Optional[int] = Field(None, ge=1, le=10, description="Średnia ocena potencjału")
    
    model_config = ConfigDict(from_attributes=True)


# Import cykliczny - rozwiązanie dla typowania
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .session import Session

# Aktualizacja modelu po imporcie
# ClientWithSessions.model_rebuild()  # Przeniesione do __init__.py po wszystkich importach
