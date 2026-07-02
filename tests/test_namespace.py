from __future__ import annotations

import asyncio
from typing import Any, cast

import pytest
from quart import Quart

from quart_socketio import Namespace


class FakeNamespaceSocketIO:
    def __init__(self) -> None:
        self.emitted: list[dict[str, Any]] = []
        self.sent: list[dict[str, Any]] = []
        self.closed_rooms: list[dict[str, Any]] = []
        self.request_kwargs: dict[str, Any] | None = None
        self.websocket_kwargs: dict[str, Any] | None = None

    async def emit(self, **kwargs: Any) -> None:
        self.emitted.append(kwargs)

    async def send(self, **kwargs: Any) -> None:
        self.sent.append(kwargs)

    async def close_room(self, **kwargs: Any) -> None:
        self.closed_rooms.append(kwargs)

    async def make_request(self, **kwargs: Any) -> str:
        self.request_kwargs = kwargs
        return "request"

    async def make_websocket(self, **kwargs: Any) -> str:
        self.websocket_kwargs = kwargs
        return "websocket"


class FakeNamespaceServer:
    not_handled = object()

    def __init__(self) -> None:
        self.saved_sessions: list[dict[str, Any]] = []

    async def save_session(self, **kwargs: Any) -> None:
        self.saved_sessions.append(kwargs)


def test_namespace_reports_asyncio_based() -> None:
    assert Namespace("/chat").is_asyncio_based() is True


@pytest.mark.asyncio
async def test_namespace_make_request_and_websocket_delegate() -> None:
    socketio = FakeNamespaceSocketIO()
    namespace = Namespace("/chat", socketio=cast("Any", socketio))

    assert await namespace.make_request(sid="sid-1") == "request"
    assert await namespace.make_websocket(sid="sid-1") == "websocket"
    assert socketio.request_kwargs == {"sid": "sid-1"}
    assert socketio.websocket_kwargs == {"sid": "sid-1"}


@pytest.mark.asyncio
async def test_namespace_trigger_event_returns_not_handled() -> None:
    namespace = Namespace("/chat")
    server = FakeNamespaceServer()
    namespace.server = cast("Any", server)

    result = await namespace.trigger_event(
        sid="sid-1",
        event="missing",
        namespace="/chat",
        environ={},
        data={},
    )

    assert result is server.not_handled


@pytest.mark.asyncio
async def test_namespace_trigger_event_calls_handler() -> None:
    namespace = Namespace("/chat")
    handled: list[dict[str, Any]] = []

    async def fake_handle_event(**kwargs: Any) -> str:
        await asyncio.sleep(0)
        handled.append(kwargs)
        return "handled"

    def on_message(body: str) -> str:
        return body

    cast("Any", namespace)._handle_event = fake_handle_event
    cast("Any", namespace).on_message = on_message

    result = await namespace.trigger_event(
        sid="sid-2",
        event="message",
        namespace="/chat",
        environ={"PATH_INFO": "/socket.io"},
        data={"body": "hello"},
    )

    assert result == "handled"
    assert handled[0]["handler"] is on_message
    assert handled[0]["data"] == {"body": "hello"}


@pytest.mark.asyncio
async def test_namespace_handle_event_disconnect_sync_and_async() -> None:
    namespace = Namespace("/chat")
    namespace.sockio_mw = cast(
        "Any",
        type("Middleware", (), {"quart_app": Quart(__name__)})(),
    )

    def sync_handler(value: str) -> str:
        return value

    async def async_handler(value: str) -> str:
        await asyncio.sleep(0)
        return value

    assert (
        await namespace._handle_event(
            data={"value": "sync"},
            event="disconnect",
            namespace="/chat",
            sid="sid-3",
            handler=sync_handler,
        )
        == "sync"
    )
    assert (
        await namespace._handle_event(
            data={"value": "async"},
            event="disconnect",
            namespace="/chat",
            sid="sid-3",
            handler=async_handler,
        )
        == "async"
    )


@pytest.mark.asyncio
async def test_namespace_emit_send_close_room_and_save_session() -> None:
    socketio = FakeNamespaceSocketIO()
    server = FakeNamespaceServer()
    namespace = Namespace("/chat", socketio=cast("Any", socketio))
    namespace.server = cast("Any", server)

    await namespace.emit("event", {"ok": True}, room="room-1")
    await namespace.send({"ok": True}, room="room-1")
    await namespace.close_room("room-1")
    await namespace.save_session("sid-4", {"user": "ada"})  # type: ignore[arg-type]

    assert socketio.emitted == [
        {
            "event": "event",
            "data": {"ok": True},
            "room": "room-1",
            "include_self": True,
            "namespace": "/chat",
            "callback": None,
        },
    ]
    assert socketio.sent == [
        {
            "data": {"ok": True},
            "room": "room-1",
            "include_self": True,
            "namespace": "/chat",
            "callback": None,
        },
    ]
    assert socketio.closed_rooms == [
        {"room": "room-1", "namespace": "/chat"},
    ]
    assert server.saved_sessions == [
        {"sid": "sid-4", "session": {"user": "ada"}, "namespace": "/chat"},
    ]


def test_namespace_get_handler_uses_on_prefix() -> None:
    namespace = Namespace("/chat")

    def on_refresh() -> None:
        pass

    namespace.on_refresh = on_refresh  # pyright: ignore[reportAttributeAccessIssue]

    assert namespace.get_handler("refresh") is on_refresh
    assert namespace.get_handler("missing") is None
