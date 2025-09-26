"""Unit tests for the public helpers exposed by ``app.services.ai_service``."""

from __future__ import annotations

import asyncio
from typing import Any, Dict

import pytest

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from app.services import ai_service


class _StubAIService:
    """Lightweight stub used to emulate the unified AI service."""

    def __init__(self, payload: Dict[str, Any] | None = None, *, raise_error: bool = False) -> None:
        self.payload = payload or {"quick_response": "Test response"}
        self.raise_error = raise_error
        self.calls: list[Dict[str, Any]] = []

    async def generate_analysis(self, **kwargs: Any) -> Dict[str, Any]:
        """Record the call and return the configured payload."""

        self.calls.append(kwargs)
        if self.raise_error:
            raise RuntimeError("boom")
        await asyncio.sleep(0)
        return self.payload


@pytest.mark.asyncio
async def test_generate_sales_analysis_returns_fallback_when_service_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The helper should never raise when the unified service is missing."""

    monkeypatch.setattr(ai_service, "ai_service_unified", None, raising=False)

    result = await ai_service.generate_sales_analysis(
        user_input="Hello",
        client_profile={},
        session_history=[],
        session_context={},
    )

    assert result["is_fallback"] is True
    assert result["error_code"] == "SERVICE_NOT_INITIALIZED"


@pytest.mark.asyncio
async def test_generate_sales_analysis_forwards_arguments(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure arguments are forwarded to the unified orchestrator."""

    stub = _StubAIService(payload={"quick_response": "ok"})
    monkeypatch.setattr(ai_service, "ai_service_unified", stub, raising=False)

    result = await ai_service.generate_sales_analysis(
        user_input="Need help",
        client_profile={"alias": "Test"},
        session_history=[{"content": "hi"}],
        session_context={"status": "active"},
    )

    assert result == {"quick_response": "ok"}
    assert stub.calls[0]["user_input"] == "Need help"
    assert stub.calls[0]["client_profile"] == {"alias": "Test"}


@pytest.mark.asyncio
async def test_generate_sales_analysis_handles_exceptions(monkeypatch: pytest.MonkeyPatch) -> None:
    """Errors bubbling from the orchestrator should be converted into fallbacks."""

    stub = _StubAIService(raise_error=True)
    monkeypatch.setattr(ai_service, "ai_service_unified", stub, raising=False)

    result = await ai_service.generate_sales_analysis(
        user_input="Need help",
        client_profile={},
        session_history=[],
        session_context={},
    )

    assert result["is_fallback"] is True
    assert result["error_code"] == "ANALYSIS_PROCESSING_ERROR"
