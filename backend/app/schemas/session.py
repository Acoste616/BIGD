from pydantic import BaseModel, ConfigDict
from typing import Optional, List
import datetime
from .interaction import Interaction

class SessionBase(BaseModel):
    pass

class SessionCreate(SessionBase):
    client_id: int

class SessionCreateNested(SessionBase):
    pass

class SessionUpdate(SessionBase):
    pass

class SessionEnd(SessionBase):
    pass

class Session(SessionBase):
    id: int
    client_id: int
    is_active: int
    start_timestamp: datetime.datetime
    end_timestamp: Optional[datetime.datetime] = None
    interactions: List[Interaction] = []
    status: str
    outcome_data: Optional[dict] = None
    
    # NOWA ARCHITEKTURA v3.0: SESSION-LEVEL CUMULATIVE PSYCHOLOGY
    cumulative_psychology: Optional[dict] = None
    psychology_confidence: Optional[int] = None
    active_clarifying_questions: Optional[List[dict]] = None
    customer_archetype: Optional[dict] = None
    psychology_updated_at: Optional[datetime.datetime] = None
    
    # MODUŁ 4: Zaawansowane Wskaźniki Sprzedażowe
    sales_indicators: Optional[dict] = None
    
    # FAZA 1 ULTRA MÓZGU: Pole dla przyszłego Syntezatora
    holistic_psychometric_profile: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)

class SessionWithClient(Session):
    """Schemat sesji z klientem"""
    model_config = ConfigDict(from_attributes=True)

class SessionWithInteractions(Session):
    """Schemat sesji z interakcjami"""
    model_config = ConfigDict(from_attributes=True)

class SessionDemo(Session):
    """Schemat sesji dla demo"""
    model_config = ConfigDict(from_attributes=True)

class SessionSummary(BaseModel):
    id: int
    client_id: int
    start_timestamp: datetime.datetime
    status: str
    
    model_config = ConfigDict(from_attributes=True)

class SessionAnalytics(BaseModel):
    """Schemat analityki sesji"""
    id: int
    
    model_config = ConfigDict(from_attributes=True)