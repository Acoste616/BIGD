"""Pydantic models used by streaming endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class StreamMessage(BaseModel):
    """Represents a single message exchanged during a streaming session."""

    role: Literal["user", "assistant", "system"] = Field(
        ...,
        description="Author of the message.",
    )
    content: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Plain text content of the message.",
    )
    timestamp: Optional[datetime] = Field(
        default=None,
        description="Optional timestamp provided by the caller.",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary metadata used by the client application.",
    )


class SessionStreamRequest(BaseModel):
    """Payload used to request an AI streaming analysis for a session."""

    user_input: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Latest message from the customer that requires an answer.",
    )
    session_history: List[StreamMessage] = Field(
        default_factory=list,
        description="Chronological history of previous messages.",
    )

    @field_validator("session_history")
    @classmethod
    def limit_history_size(cls, value: List[StreamMessage]) -> List[StreamMessage]:
        """Keep only the most recent messages to protect the model context."""

        max_items = 50
        if len(value) > max_items:
            return value[-max_items:]
        return value


class DojoMessageCreate(BaseModel):
    """Minimal payload used by the internal AI Dojo training interface."""

    content: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Message composed by the trainer.",
    )
