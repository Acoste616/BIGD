"""Streaming endpoints for AI powered analysis."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, AsyncGenerator, Dict, Iterable, List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Request,
    status,
)
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.session_repository import SessionRepository
from app.schemas.stream import DojoMessageCreate, SessionStreamRequest, StreamMessage
from app.services.ai_service import generate_sales_analysis

logger = logging.getLogger(__name__)

router = APIRouter(tags=["stream"])


DEFAULT_FALLBACK_RESPONSE = "I am sorry, I am unable to provide a response at the moment."


def _get_session_repository() -> SessionRepository:
    """Return a new ``SessionRepository`` instance."""

    return SessionRepository()


def _serialize_session_history(history: Iterable[StreamMessage]) -> List[Dict[str, Any]]:
    """Convert validated history entries into serialisable dictionaries."""

    return [entry.model_dump(mode="json") for entry in history]


def _extract_quick_response_text(analysis_result: Dict[str, Any]) -> str:
    """Return the human friendly response text from an AI analysis payload."""

    quick_response = analysis_result.get("quick_response")

    if isinstance(quick_response, dict):
        # Unified responses frequently expose the text under ``text`` or ``content``.
        for key in ("text", "content", "message"):
            if isinstance(quick_response.get(key), str) and quick_response[key].strip():
                return quick_response[key]

    if isinstance(quick_response, str) and quick_response.strip():
        return quick_response

    return DEFAULT_FALLBACK_RESPONSE


async def stream_sales_analysis(
    *,
    user_input: str,
    client_profile: Dict[str, Any],
    session_history: List[Dict[str, Any]],
    session_context: Dict[str, Any],
) -> AsyncGenerator[str, None]:
    """Stream analysis events token by token for the provided conversation data."""

    try:
        analysis_result = await generate_sales_analysis(
            user_input=user_input,
            client_profile=client_profile,
            session_history=session_history,
            session_context=session_context,
        )
    except Exception as exc:  # pragma: no cover - defensive guard
        logger.exception("Failed to generate sales analysis", exc_info=exc)
        yield _format_event("error", str(exc))
        return

    quick_response_text = _extract_quick_response_text(analysis_result)
    tokens = quick_response_text.split()

    for index, token in enumerate(tokens, start=1):
        yield _format_event("token", _append_space(token, index, len(tokens)))
        # Short delay to emulate live streaming while remaining test friendly.
        await asyncio.sleep(0.05)

    yield _format_event(
        "stream_end",
        json.dumps(analysis_result, default=str),
    )


def _append_space(token: str, index: int, total: int) -> str:
    """Append a space to ``token`` if there are more tokens to follow."""

    return token + (" " if index < total else "")


def _format_event(event: str, data: str) -> str:
    """Format a Server Sent Event payload."""

    safe_data = data.replace("\n", " ")
    return f'data: {{"event": "{event}", "data": "{safe_data}"}}\n\n'


def _build_client_profile(session) -> Dict[str, Any]:
    """Build a minimal client profile for the orchestrator."""

    client = getattr(session, "client", None)

    if client is None:
        return {
            "alias": "Unknown client",
            "archetype": "Undiscovered",  # Fallback used by downstream prompts.
            "tags": [],
            "notes": None,
        }

    return {
        "alias": getattr(client, "alias", "Unknown client") or "Unknown client",
        "archetype": getattr(client, "archetype", None) or "Undiscovered",
        "notes": getattr(client, "notes", None),
        "created_at": getattr(client, "created_at", None),
        "updated_at": getattr(client, "updated_at", None),
    }


async def _load_session(
    db: AsyncSession,
    session_repo: SessionRepository,
    session_id: int,
) -> Any:
    """Fetch a session instance and make sure the related client is loaded."""

    session = await session_repo.get_session(db, session_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    try:
        await db.refresh(session, attribute_names=["client"])
    except Exception:  # pragma: no cover - SQLAlchemy relationship safety net
        logger.debug("Client relationship could not be refreshed for session %s", session_id)

    return session


@router.post(
    "/sessions/{session_id}/interactions/stream",
    summary="Stream AI analysis for a session",
)
async def stream_session_interaction(
    request_data: SessionStreamRequest,
    request: Request,  # noqa: ARG001 - FastAPI injects request context for middleware hooks
    session_id: int = Path(..., ge=1, description="Identifier of the target session"),
    db: AsyncSession = Depends(get_db),
    session_repo: SessionRepository = Depends(_get_session_repository),
):
    """Stream a live AI response for a particular sales session."""

    session = await _load_session(db, session_repo, session_id)

    client_profile = _build_client_profile(session)
    serialized_history = _serialize_session_history(request_data.session_history)

    analysis_generator = stream_sales_analysis(
        user_input=request_data.user_input,
        client_profile=client_profile,
        session_history=serialized_history,
        session_context={
            "session_id": session.id,
            "status": getattr(session, "status", "unknown"),
            "started_at": getattr(session, "start_timestamp", None),
        },
    )

    return StreamingResponse(analysis_generator, media_type="text/event-stream")


@router.post(
    "/dojo/chat/stream",
    summary="Stream AI response for the training dojo",
)
async def stream_dojo_chat(
    request_data: DojoMessageCreate,
    request: Request,  # noqa: ARG001 - reserved for future middleware hooks
):
    """Stream an AI response for the internal training dojo interface."""

    analysis_generator = stream_sales_analysis(
        user_input=request_data.content,
        client_profile={"archetype": "Sales Expert"},
        session_history=[],
        session_context={"session_type": "dojo_training"},
    )

    return StreamingResponse(analysis_generator, media_type="text/event-stream")
