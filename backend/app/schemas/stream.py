from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any


class SessionStreamRequest(BaseModel):
    """
    Schema for streaming AI analysis requests for a session.
    """
    user_input: str
    session_history: Optional[List[Dict[str, Any]]] = None

    model_config = ConfigDict(from_attributes=True)


class DojoMessageCreate(BaseModel):
    """
    Schema for creating a message in the AI Dojo chat.
    """
    content: str

    model_config = ConfigDict(from_attributes=True)