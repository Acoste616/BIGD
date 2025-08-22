"""
Moduł schematów Pydantic - eksport wszystkich schematów API
"""

# Client schemas
from .client import (
    ClientBase,
    ClientCreate,
    ClientUpdate,
    Client,
    ClientWithSessions,
    ClientSummary
)

# Session schemas
from .session import (
    SessionBase,
    SessionCreate,
    SessionCreateNested,
    SessionUpdate,
    SessionEnd,
    Session,
    SessionWithClient,
    SessionWithInteractions,
    SessionDemo,
    SessionSummary,
    SessionAnalytics
)

# Interaction schemas
from .interaction import (
    InteractionBase,
    InteractionCreate,
    InteractionUpdate,
    Interaction,
    InteractionWithFeedback,
    InteractionWithContext,
    InteractionResponse,
    InteractionRequest
)

# Feedback schemas
from .feedback import (
    FeedbackCreate,
)



__all__ = [
    # Client
    "ClientBase",
    "ClientCreate",
    "ClientUpdate",
    "Client",
    "ClientWithSessions",
    "ClientSummary",
    
    # Session
    "SessionBase",
    "SessionCreate",
    "SessionCreateNested", 
    "SessionUpdate",
    "SessionEnd",
    "Session",
    "SessionWithClient",
    "SessionWithInteractions",
    "SessionDemo",
    "SessionSummary",
    "SessionAnalytics",
    
    # Interaction
    "InteractionBase",
    "InteractionCreate",
    "InteractionUpdate",
    "Interaction",
    "InteractionWithFeedback",
    "InteractionWithContext",
    "InteractionResponse",
    "InteractionRequest",
    
    # Feedback
    "FeedbackCreate",
]
