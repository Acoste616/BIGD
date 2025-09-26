"""Tests for the streaming router."""

from __future__ import annotations

from typing import Any, Dict

import importlib.util
import sys
from pathlib import Path

import pytest

backend_root = Path(__file__).resolve().parents[2]
sys.path.append(str(backend_root))

stream_path = backend_root / "app" / "routers" / "stream.py"
spec = importlib.util.spec_from_file_location("stream_module", stream_path)
stream = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(stream)  # type: ignore[union-attr]

from app.schemas.stream import SessionStreamRequest, StreamMessage


@pytest.fixture(autouse=True)
def _fast_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    """Accelerate ``asyncio.sleep`` to keep the tests snappy."""

    async def _fake_sleep(_: float) -> None:  # pragma: no cover - trivial stub
        return None

    monkeypatch.setattr(stream.asyncio, "sleep", _fake_sleep)


@pytest.mark.asyncio
async def test_stream_sales_analysis_yields_tokens(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure the generator emits token events followed by a terminal payload."""

    async def _fake_generate_sales_analysis(**_: Any) -> Dict[str, Any]:
        return {"quick_response": "hello world"}

    monkeypatch.setattr(stream, "generate_sales_analysis", _fake_generate_sales_analysis)

    generator = stream.stream_sales_analysis(
        user_input="hello",
        client_profile={},
        session_history=[],
        session_context={},
    )

    events = [event async for event in generator]

    assert events[0].startswith('data: {"event": "token"')
    assert events[-1].startswith('data: {"event": "stream_end"')


@pytest.mark.asyncio
async def test_stream_sales_analysis_handles_exceptions(monkeypatch: pytest.MonkeyPatch) -> None:
    """Errors from the AI layer should be converted into an error event."""

    async def _failing_generate_sales_analysis(**_: Any) -> Dict[str, Any]:
        raise RuntimeError("downstream failure")

    monkeypatch.setattr(stream, "generate_sales_analysis", _failing_generate_sales_analysis)

    generator = stream.stream_sales_analysis(
        user_input="hello",
        client_profile={},
        session_history=[],
        session_context={},
    )

    events = [event async for event in generator]

    assert events == ['data: {"event": "error", "data": "downstream failure"}\n\n']


def test_session_stream_request_limits_history() -> None:
    """Validation should truncate excessive history entries."""

    history = [StreamMessage(role="user", content=f"{i}") for i in range(60)]
    request = SessionStreamRequest(user_input="hello", session_history=history)
    assert len(request.session_history) == 50
