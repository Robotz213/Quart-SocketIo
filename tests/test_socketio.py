from __future__ import annotations

import asyncio
from typing import Any, cast

import pytest
from quart import Quart

from quart_socketio import Namespace, SocketIO
from quart_socketio.common.exceptions import QuartValueError


class DummyServer:
    not_handled = object()

    def __init__(self) -> None:
        self.emitted: list[dict[str, Any]] = []
        self.calls: list[dict[str, Any]] = []
        self.closed_rooms: list[tuple[str, str | None]] = []
        self.namespace_handlers: dict[str, Namespace] = {}
        self.environ: dict[tuple[str, str], dict[str, Any]] = {}
        self.started_task: tuple[Any, tuple[Any, ...], dict[str, Any]] | None
        self.started_task = None
        self.sleep_seconds: float | None = None

    def get_environ(self, sid: str, namespace: str) -> dict[str, Any]:
        return self.environ.get((sid, namespace), {})

    async def emit(self, **kwargs: Any) -> None:
        self.emitted.append(kwargs)

    async def call(
        self,
        event: str,
        *args: Any,
        **kwargs: Any,
    ) -> dict[str, Any]:
        payload = {"event": event, "args": args, **kwargs}
        self.calls.append(payload)
        return payload

    async def close_room(
        self,
        room: str,
        namespace: str | None = None,
    ) -> None:
        self.closed_rooms.append((room, namespace))

    def start_background_task(
        self,
        target: Any,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        self.started_task = (target, args, kwargs)
        return "task"

    def sleep(self, seconds: float = 0) -> float:
        self.sleep_seconds = seconds
        return seconds


@pytest.mark.asyncio
async def test_trigger_event_dispatches_registered_handler() -> None:
    socketio = SocketIO()
    server = DummyServer()
    socketio.server = cast("Any", server)
    handled: dict[str, Any] = {}

    async def fake_handle_event(**kwargs: Any) -> dict[str, Any]:
        await asyncio.sleep(0)
        handled.update(kwargs)
        return {"ok": True}

    cast("Any", socketio)._handle_event = fake_handle_event

    @socketio.on("chat", namespace="/room")
    def chat(data: dict[str, Any]) -> dict[str, Any]:
        return data

    environ = {"REQUEST_METHOD": "GET"}
    socketio.environments["sid-1"] = environ
    result = await socketio._trigger_event(
        "chat",
        "/room",
        "sid-1",
        environ,
        {"text": "hello"},
    )

    assert result == {"ok": True}
    assert handled["handler"] is chat
    assert handled["event"] == "chat"
    assert handled["namespace"] == "/room"
    assert handled["sid"] == "sid-1"
    assert handled["environ"] == environ
    assert handled["data"] == {"text": "hello"}


@pytest.mark.asyncio
async def test_trigger_event_stores_connect_environ() -> None:
    socketio = SocketIO()
    server = DummyServer()
    socketio.server = cast("Any", server)
    environ = {"PATH_INFO": "/socket.io"}

    result = await socketio._trigger_event("connect", "/", "sid-2", environ)

    assert result is socketio.server.not_handled
    assert socketio.environments["sid-2"] == environ
    assert socketio.enviroments is socketio.environments


@pytest.mark.asyncio
async def test_trigger_event_forwards_to_namespace_handler() -> None:
    socketio = SocketIO()
    server = DummyServer()
    socketio.server = cast("Any", server)
    namespace = Namespace("/chat")
    namespace_calls: list[dict[str, Any]] = []

    async def trigger_event(**kwargs: Any) -> str:
        await asyncio.sleep(0)
        namespace_calls.append(kwargs)
        return "handled-by-namespace"

    cast("Any", namespace).trigger_event = trigger_event
    socketio.environments["sid-3"] = {"REQUEST_METHOD": "GET"}
    server.namespace_handlers["/chat"] = namespace

    result = await socketio._trigger_event(
        "message",
        "/chat",
        "sid-3",
        {"REQUEST_METHOD": "GET"},
        {"body": "hi"},
    )

    assert result == "handled-by-namespace"
    assert namespace_calls[0]["event"] == "message"
    assert namespace_calls[0]["namespace"] == "/chat"
    assert namespace_calls[0]["sid"] == "sid-3"
    assert namespace_calls[0]["data"] == {"body": "hi"}


def test_event_decorator_registers_function_name() -> None:
    socketio = SocketIO()

    @socketio.event
    def status(data: dict[str, Any]) -> dict[str, Any]:
        return data

    assert socketio.config["handlers"][0][0] == "status"
    assert socketio.config["handlers"][0][2] == "/"
    assert socketio.config["handlers"][0][1].__name__ == "status"


def test_event_decorator_accepts_custom_namespace() -> None:
    socketio = SocketIO()

    @socketio.event(namespace="/admin")
    def refresh(data: dict[str, Any]) -> dict[str, Any]:
        return data

    assert socketio.config["handlers"][0][0] == "refresh"
    assert socketio.config["handlers"][0][2] == "/admin"


def test_on_event_registers_handler_without_decorator_syntax() -> None:
    socketio = SocketIO()

    def refresh(data: dict[str, Any]) -> dict[str, Any]:
        return data

    socketio.on_event("refresh", refresh, namespace="/admin")

    assert socketio.config["handlers"][0][0] == "refresh"
    assert socketio.config["handlers"][0][2] == "/admin"


def test_error_handlers_are_registered_and_validated() -> None:
    socketio = SocketIO()

    @socketio.on_error(namespace="/chat")
    def chat_error(exc: Exception) -> str:
        return str(exc)

    @socketio.on_error_default
    def default_error(exc: Exception) -> str:
        return str(exc)

    assert socketio.config["exception_handlers"]["/chat"] is chat_error
    assert socketio.config["default_exception_handler"] is default_error

    with pytest.raises(QuartValueError, match="exception_handler"):
        socketio.on_error()("not-callable")  # pyright: ignore[reportArgumentType]

    with pytest.raises(QuartValueError, match="exception_handler"):
        socketio.on_error_default("not-callable")  # pyright: ignore[reportArgumentType]


@pytest.mark.asyncio
async def test_emit_delegates_to_underlying_server() -> None:
    socketio = SocketIO()
    server = DummyServer()
    socketio.server = cast("Any", server)

    await socketio.emit(
        "notification",
        {"kind": "manual"},
        to="sid-4",
        namespace="/chat",
        ignore_queue=True,
    )

    assert server.emitted == [
        {
            "event": "notification",
            "data": {"kind": "manual"},
            "to": "sid-4",
            "room": None,
            "skip_sid": None,
            "namespace": "/chat",
            "callback": None,
            "ignore_queue": True,
        },
    ]


@pytest.mark.asyncio
async def test_call_delegates_to_underlying_server() -> None:
    socketio = SocketIO()
    server = DummyServer()
    socketio.server = cast("Any", server)

    result = await socketio.call(
        "status",
        {"check": True},
        room="sid-5",
        namespace="/ops",
        timeout=5,
        ignore_queue=True,
    )

    assert result == {
        "event": "status",
        "args": ({"check": True},),
        "namespace": "/ops",
        "to": "sid-5",
        "timeout": 5,
        "ignore_queue": True,
    }


@pytest.mark.asyncio
async def test_send_uses_json_or_message_event() -> None:
    socketio = SocketIO()
    emitted: list[dict[str, Any]] = []

    async def emit(*args: Any, **kwargs: Any) -> None:
        await asyncio.sleep(0)
        emitted.append({"args": args, **kwargs})

    cast("Any", socketio).emit = emit

    await socketio.send(data={"ok": True}, json=True, namespace="/api")
    await socketio.send(data="hello", namespace="/api")

    assert emitted == [
        {
            "args": ("json", {"ok": True}),
            "namespace": "/api",
            "to": None,
            "skip_sid": None,
            "callback": None,
        },
        {
            "args": ("message", "hello"),
            "namespace": "/api",
            "to": None,
            "skip_sid": None,
            "callback": None,
        },
    ]


@pytest.mark.asyncio
async def test_close_room_delegates_to_underlying_server() -> None:
    socketio = SocketIO()
    server = DummyServer()
    socketio.server = cast("Any", server)

    await socketio.close_room("room-1", namespace="/chat")

    assert server.closed_rooms == [("room-1", "/chat")]


def test_background_task_and_sleep_delegate_to_server() -> None:
    socketio = SocketIO()
    server = DummyServer()
    socketio.server = cast("Any", server)

    def task(name: str) -> str:
        return name

    assert socketio.start_background_task(task, "sync", named=True) == "task"
    assert server.started_task == (task, ("sync",), {"named": True})
    assert socketio.sleep(1.5) == pytest.approx(1.5)
    assert server.sleep_seconds == pytest.approx(1.5)


def test_init_app_installs_socketio_extension_and_middleware() -> None:
    app = Quart(__name__)

    socketio = SocketIO(app=app, cors_allowed_origins=[])

    assert app.extensions["socketio"] is socketio
    assert socketio.sockio_mw.quart_app is app
    assert socketio.server.async_mode == "asgi"


def test_on_namespace_registers_namespace_handler() -> None:
    app = Quart(__name__)
    socketio = SocketIO(app=app, cors_allowed_origins=[])
    namespace = Namespace("/chat")

    socketio.on_namespace(namespace)

    assert namespace.socketio is socketio
    assert namespace in socketio.config["namespace_handlers"]


def test_on_namespace_rejects_non_namespace() -> None:
    socketio = SocketIO()

    with pytest.raises(QuartValueError, match="Not a namespace instance"):
        socketio.on_namespace(object())  # pyright: ignore[reportArgumentType]
