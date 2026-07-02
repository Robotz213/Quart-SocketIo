from __future__ import annotations

from typing import Any, cast

import pytest
from quart import Quart, request

from quart_socketio import utils


class FakeContextServer:
    def __init__(self) -> None:
        self.entered_rooms: list[tuple[str, str, str | None]] = []
        self.left_rooms: list[tuple[str, str, str | None]] = []
        self.closed_rooms: list[tuple[str, str | None]] = []
        self.disconnected: list[tuple[str, str | None]] = []

    async def enter_room(
        self,
        sid: str,
        room: str,
        namespace: str | None = None,
    ) -> None:
        self.entered_rooms.append((sid, room, namespace))

    async def leave_room(
        self,
        sid: str,
        room: str,
        namespace: str | None = None,
    ) -> None:
        self.left_rooms.append((sid, room, namespace))

    async def close_room(
        self,
        room: str,
        namespace: str | None = None,
    ) -> None:
        self.closed_rooms.append((room, namespace))

    def rooms(self, sid: str, namespace: str | None = None) -> list[str]:
        return [sid, namespace or "/", "lobby"]

    async def disconnect(
        self,
        sid: str,
        namespace: str | None = None,
    ) -> str:
        self.disconnected.append((sid, namespace))
        return "disconnected"


class FakeContextSocketIO:
    def __init__(self) -> None:
        self.server = FakeContextServer()
        self.emitted: list[dict[str, Any]] = []
        self.calls: list[dict[str, Any]] = []
        self.sent: list[dict[str, Any]] = []

    async def emit(self, event: str, *args: Any, **kwargs: Any) -> None:
        self.emitted.append({"event": event, "args": args, **kwargs})

    async def call(self, event: str, *args: Any, **kwargs: Any) -> str:
        self.calls.append({"event": event, "args": args, **kwargs})
        return "ack"

    async def send(self, **kwargs: Any) -> None:
        self.sent.append(kwargs)


@pytest.fixture
def app_with_socketio() -> Quart:
    app = Quart(__name__)
    app.extensions = {"socketio": FakeContextSocketIO()}
    return app


@pytest.mark.asyncio
async def test_context_emit_defaults_to_request_sid(
    app_with_socketio: Quart,
) -> None:
    async with app_with_socketio.test_request_context("/"):
        cast("Any", request).sid = "sid-1"
        cast("Any", request).namespace = "/chat"

        await utils.emit("reply", {"ok": True})

    socketio = app_with_socketio.extensions["socketio"]
    assert socketio.emitted == [
        {
            "event": "reply",
            "args": ({"ok": True},),
            "namespace": "/chat",
            "to": "sid-1",
            "include_self": True,
            "skip_sid": None,
            "callback": None,
            "ignore_queue": False,
        },
    ]


@pytest.mark.asyncio
async def test_context_emit_respects_broadcast_and_room(
    app_with_socketio: Quart,
) -> None:
    async with app_with_socketio.test_request_context("/"):
        cast("Any", request).sid = "sid-2"
        cast("Any", request).namespace = "/chat"

        await utils.emit(
            "news",
            namespace="/custom",
            room="room-1",
            broadcast=True,
            include_self=False,
            skip_sid="sid-3",
            ignore_queue=True,
        )

    socketio = app_with_socketio.extensions["socketio"]
    assert socketio.emitted[0]["namespace"] == "/custom"
    assert socketio.emitted[0]["to"] == "room-1"
    assert socketio.emitted[0]["include_self"] is False
    assert socketio.emitted[0]["skip_sid"] == "sid-3"
    assert socketio.emitted[0]["ignore_queue"] is True


@pytest.mark.asyncio
async def test_context_call_defaults_to_request_sid(
    app_with_socketio: Quart,
) -> None:
    async with app_with_socketio.test_request_context("/"):
        cast("Any", request).sid = "sid-4"
        cast("Any", request).namespace = "/ops"

        result = await utils.call("status", {"ping": True}, timeout=5)

    socketio = app_with_socketio.extensions["socketio"]
    assert result == "ack"
    assert socketio.calls == [
        {
            "event": "status",
            "args": ({"ping": True},),
            "namespace": "/ops",
            "to": "sid-4",
            "ignore_queue": False,
            "timeout": 5,
        },
    ]


@pytest.mark.asyncio
async def test_context_send_delegates_to_extension(
    app_with_socketio: Quart,
) -> None:
    async with app_with_socketio.test_request_context("/"):
        cast("Any", request).sid = "sid-5"
        cast("Any", request).namespace = "/chat"

        await utils.send({"ok": True}, json=True, room="room-2")

    socketio = app_with_socketio.extensions["socketio"]
    assert socketio.sent == [
        {
            "data": {"ok": True},
            "json": True,
            "namespace": "/chat",
            "to": "room-2",
            "include_self": True,
            "skip_sid": None,
            "callback": None,
            "ignore_queue": False,
        },
    ]


@pytest.mark.asyncio
async def test_room_helpers_use_request_context(
    app_with_socketio: Quart,
) -> None:
    async with app_with_socketio.test_request_context("/"):
        cast("Any", request).sid = "sid-6"
        cast("Any", request).namespace = "/chat"

        await utils.join_room("room-3")
        await utils.leave_room("room-3")
        await utils.close_room("room-3")
        current_rooms = utils.rooms()
        result = await utils.disconnect()

    server = app_with_socketio.extensions["socketio"].server
    assert server.entered_rooms == [("sid-6", "room-3", "/chat")]
    assert server.left_rooms == [("sid-6", "room-3", "/chat")]
    assert server.closed_rooms == [("room-3", "/chat")]
    assert server.disconnected == [("sid-6", "/chat")]
    assert current_rooms == ["sid-6", "/chat", "lobby"]
    assert result == "disconnected"
