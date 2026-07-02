from __future__ import annotations

from typing import Any, cast

import pytest
from quart import Quart

from quart_socketio import Namespace, SocketIO
from quart_socketio.common.exceptions import QuartRuntimeError, QuartValueError
from quart_socketio.core import EnvironError


def make_environ() -> dict[str, Any]:
    return {
        "REQUEST_METHOD": "GET",
        "PATH_INFO": "/socket.io",
        "SERVER_PROTOCOL": "1.1",
        "HTTP_AUTHORIZATION": b"Bearer token",
        "asgi.scope": {
            "headers": [(b"x-custom", b"value")],
            "query_string": b"token=1",
            "scheme": "https",
            "root_path": "",
        },
        "nested": {"x-nested": "nested-value"},
    }


def test_load_headers_decodes_asgi_and_wsgi_headers() -> None:
    headers = SocketIO.load_headers(make_environ())

    assert headers["X-Custom"] == "value"
    assert headers["Authorization"] == "Bearer token"
    assert headers["X-Nested"] == "nested-value"


@pytest.mark.asyncio
async def test_make_request_adds_socketio_attributes() -> None:
    socketio = SocketIO()

    request = await socketio.make_request(
        environ=make_environ(),
        sid="sid-1",
        namespace="/chat",
    )

    assert request.method == "GET"
    assert request.path == "/socket.io"
    assert cast("Any", request).sid == "sid-1"
    assert cast("Any", request).namespace == "/chat"
    assert request.headers["X-Custom"] == "value"


@pytest.mark.asyncio
async def test_make_websocket_raises_when_environ_is_missing() -> None:
    socketio = SocketIO()

    class Server:
        def get_environ(self, sid: str, namespace: str) -> dict[str, Any]:
            return {}

    socketio.server = cast("Any", Server())

    with pytest.raises(EnvironError):
        await socketio.make_websocket(sid="sid-2", namespace="/chat")


@pytest.mark.asyncio
async def test_make_websocket_adds_sid_when_environ_exists() -> None:
    socketio = SocketIO()
    environ = make_environ()
    environ["asgi.receive"] = object()
    environ["asgi.send"] = object()
    environ["asgi.scope"].update({
        "subprotocols": ["socket.io"],
        "accept": None,
        "close": None,
    })

    class Server:
        def get_environ(self, sid: str, namespace: str) -> dict[str, Any]:
            return environ

    socketio.server = cast("Any", Server())

    websocket = await socketio.make_websocket(sid="sid-3", namespace="/chat")

    assert websocket.path == "/socket.io"
    assert cast("Any", websocket).sid == "sid-3"


@pytest.mark.asyncio
async def test_register_handler_uses_event_tuple() -> None:
    socketio = SocketIO()

    def handler(data: dict[str, Any]) -> dict[str, Any]:
        return data

    await socketio.register_handler(("refresh", handler, "/ops"))

    assert socketio.config["handlers"][0][0] == "refresh"
    assert socketio.config["handlers"][0][2] == "/ops"


def test_register_namespace_requires_initialized_server() -> None:
    socketio = SocketIO()

    with pytest.raises(QuartRuntimeError, match="not initialized"):
        socketio.register_namespace(Namespace("/chat"))


def test_register_namespace_rejects_invalid_handler() -> None:
    socketio = SocketIO()

    with pytest.raises(QuartValueError, match="Not a namespace instance"):
        socketio.register_namespace(object())  # pyright: ignore[reportArgumentType]


def test_unregister_namespace_delegates_to_server() -> None:
    socketio = SocketIO()
    namespace = Namespace("/chat")

    class Server:
        def __init__(self) -> None:
            self.unregistered: list[Namespace] = []

        def unregister_namespace(self, namespace_handler: Namespace) -> None:
            self.unregistered.append(namespace_handler)

    server = Server()
    socketio.server = cast("Any", server)
    socketio.config["namespace_handlers"].append(namespace)

    socketio.unregister_namespace(namespace)

    assert server.unregistered == [namespace]
    assert namespace not in socketio.config["namespace_handlers"]


def test_run_requires_app() -> None:
    socketio = SocketIO()

    with pytest.raises(QuartValueError, match="application instance"):
        cast("Any", socketio).run()


@pytest.mark.asyncio
async def test_json_setting_wraps_quart_json() -> None:
    app = Quart(__name__)
    socketio = SocketIO()

    socketio.json_setting(app)
    json_wrapper = socketio.config["json"]

    assert await json_wrapper.dumps({"ok": True}) == '{"ok": true}'
    assert await json_wrapper.loads('{"ok": true}') == {"ok": True}
