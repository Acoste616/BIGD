from pydantic import BaseModel, ConfigDict
from typing import Optional, List, TYPE_CHECKING
import datetime

# Import wewnątrz bloku TYPE_CHECKING, aby uniknąć zależności cyklicznej
if TYPE_CHECKING:
    from .session import Session

class ClientBase(BaseModel):
    notes: Optional[str] = None
    archetype: Optional[str] = None

class ClientCreate(ClientBase):
    alias: Optional[str] = None

class ClientUpdate(BaseModel):
    notes: Optional[str] = None
    archetype: Optional[str] = None

class Client(ClientBase):
    id: int
    alias: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    sessions: List["Session"] = []

    model_config = ConfigDict(from_attributes=True)

class ClientWithSessions(Client):
    """Schemat klienta z sesjami"""
    model_config = ConfigDict(from_attributes=True)

class ClientSummary(BaseModel):
    id: int
    alias: str
    archetype: Optional[str] = None
    sessions_count: int = 0
    has_notes: bool = False
    
    model_config = ConfigDict(from_attributes=True)