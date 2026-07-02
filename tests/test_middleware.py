from __future__ import annotations

import asyncio
from typing import Any

import pytest
from quart import Quart
from socketio import ASGIApp

from quart_socketio.middleare import (
    QuartSocketIOMiddleware as CompatMiddleware,
)
from quart_socketio.middleware import (
    QuartSocketIOMiddleware,
    _get_trusted_value,
)


async def _receive() -> dict[str, str]:
    await asyncio.sleep(0)
    return {"type": "test"}


def test_middleare_compatibility_shim_exports_middleware() -> None:
    assert CompatMiddleware is QuartSocketIOMiddleware


def test_get_trusted_value_uses_configured_hop_from_right() -> None:
    headers = [(b"x-forwarded-for", b"198.51.100.1, 203.0.113.10")]

    assert _get_trusted_value(b"x-forwarded-for", headers, 1) == (
        "203.0.113.10"
    )
    assert _get_trusted_value(b"x-forwarded-for", headers, 2) == (
        "198.51.100.1"
    )


def test_get_trusted_value_ignores_untrusted_headers() -> None:
    headers = [(b"x-forwarded-proto", b"https")]

    assert _get_trusted_value(b"x-forwarded-proto", headers, 0) is None
    assert _get_trusted_value(b"x-forwarded-host", headers, 1) is None


@pytest.mark.asyncio
async def test_middleware_applies_forwarded_header(monkeypatch: Any) -> None:
    seen_scopes: list[dict[str, Any]] = []

    async def fake_call(
        self: ASGIApp,
        scope: dict[str, Any],
        receive: Any,
        send: Any,
    ) -> None:
        await receive()
        seen_scopes.append(scope)

    monkeypatch.setattr(ASGIApp, "__call__", fake_call)
    app = Quart(__name__)
    middleware = QuartSocketIOMiddleware(
        socketio_app=object(),  # pyright: ignore[reportArgumentType]
        quart_app=app,
    )
    original_scope = {
        "type": "http",
        "client": ("127.0.0.1", 5000),
        "scheme": "http",
        "headers": [
            (b"host", b"internal"),
            (
                b"forwarded",
                b"for=203.0.113.10;proto=https;host=example.com",
            ),
        ],
    }

    await middleware(original_scope, _receive, object())

    assert seen_scopes[0]["client"] == ("203.0.113.10", 0)
    assert seen_scopes[0]["scheme"] == "https"
    assert (b"host", b"example.com") in seen_scopes[0]["headers"]
    assert original_scope["client"] == ("127.0.0.1", 5000)


@pytest.mark.asyncio
async def test_middleware_applies_x_forwarded_headers(
    monkeypatch: Any,
) -> None:
    seen_scopes: list[dict[str, Any]] = []

    async def fake_call(
        self: ASGIApp,
        scope: dict[str, Any],
        receive: Any,
        send: Any,
    ) -> None:
        await receive()
        seen_scopes.append(scope)

    monkeypatch.setattr(ASGIApp, "__call__", fake_call)
    app = Quart(__name__)
    app.config["SOCKETIO_MODE"] = "legacy"
    app.config["SOCKETIO_TRUSTED_HOPS"] = 2
    middleware = QuartSocketIOMiddleware(
        socketio_app=object(),  # pyright: ignore[reportArgumentType]
        quart_app=app,
    )
    scope = {
        "type": "websocket",
        "client": ("127.0.0.1", 5000),
        "scheme": "http",
        "headers": [
            (b"host", b"internal"),
            (b"x-forwarded-for", b"198.51.100.1, 203.0.113.10"),
            (b"x-forwarded-proto", b"http, https"),
            (b"x-forwarded-host", b"old.example.com, example.com"),
        ],
    }

    await middleware(scope, _receive, object())

    assert seen_scopes[0]["client"] == ("198.51.100.1", 0)
    assert seen_scopes[0]["scheme"] == "http"
    assert (b"host", b"old.example.com") in seen_scopes[0]["headers"]


@pytest.mark.asyncio
async def test_middleware_ignores_non_http_scopes(monkeypatch: Any) -> None:
    seen_scopes: list[dict[str, Any]] = []

    async def fake_call(
        self: ASGIApp,
        scope: dict[str, Any],
        receive: Any,
        send: Any,
    ) -> None:
        await receive()
        seen_scopes.append(scope)

    monkeypatch.setattr(ASGIApp, "__call__", fake_call)
    app = Quart(__name__)
    middleware = QuartSocketIOMiddleware(
        socketio_app=object(),  # pyright: ignore[reportArgumentType]
        quart_app=app,
    )
    scope = {"type": "lifespan", "headers": []}

    await middleware(scope, _receive, object())

    assert seen_scopes == [scope]
