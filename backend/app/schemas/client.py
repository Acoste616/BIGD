from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, TYPE_CHECKING
import datetime

# Import wewnątrz bloku TYPE_CHECKING, aby uniknąć zależności cyklicznej
if TYPE_CHECKING:
    from .session import Session

class ClientBase(BaseModel):
    notes: Optional[str] = None
    archetype: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None

class ClientCreate(ClientBase):
    alias: Optional[str] = None
    
    model_config = ConfigDict(extra="forbid")

class ClientUpdate(BaseModel):
    notes: Optional[str] = None
    archetype: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    
    model_config = ConfigDict(extra="forbid")

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