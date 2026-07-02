from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING

from socketio import ASGIApp, AsyncServer

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    from hypercorn.typing import Scope
    from quart import Quart


class QuartSocketIOMiddleware(ASGIApp):
    """Route ASGI traffic between Socket.IO and Quart."""

    def __init__(
        self,
        socketio_app: AsyncServer,
        quart_app: Quart,
        socketio_path: str = "socket.io",
    ) -> None:
        """Create the middleware wrapper.

        Args:
            socketio_app (AsyncServer): Socket.IO ASGI server.
            quart_app (Quart): Quart application.
            socketio_path (str): Socket.IO endpoint path.
        """
        self.quart_app = quart_app
        self.mode = quart_app.config.get("SOCKETIO_MODE", "modern")
        self.trusted_hops = quart_app.config.get("SOCKETIO_TRUSTED_HOPS", 1)
        super().__init__(
            socketio_app,
            quart_app.asgi_app,
            socketio_path=socketio_path,
        )

    async def __call__(
        self,
        scope: Scope,
        receive: Callable,
        send: Callable,
    ) -> None:
        """Handle an ASGI request and apply trusted proxy headers.

        Args:
            scope (Scope): ASGI connection scope.
            receive (Callable): ASGI receive callable.
            send (Callable): ASGI send callable.
        """
        host: str | None = None
        if scope["type"] == "http" or scope["type"] == "websocket":
            scope = deepcopy(scope)
            headers = scope["headers"]
            client: str | None = None
            scheme: str | None = None

            if (
                self.mode == "modern"
                and (
                    value := _get_trusted_value(
                        b"forwarded",
                        headers,
                        self.trusted_hops,
                    )
                )
                is not None
            ):
                for part in value.split(";"):
                    if part.startswith("for="):
                        client = part[4:].strip()
                    elif part.startswith("host="):
                        host = part[5:].strip()
                    elif part.startswith("proto="):
                        scheme = part[6:].strip()

            else:
                client = _get_trusted_value(
                    b"x-forwarded-for",
                    headers,
                    self.trusted_hops,
                )
                scheme = _get_trusted_value(
                    b"x-forwarded-proto",
                    headers,
                    self.trusted_hops,
                )
                host = _get_trusted_value(
                    b"x-forwarded-host",
                    headers,
                    self.trusted_hops,
                )

            if client is not None:
                scope["client"] = (client, 0)

            if scheme is not None:
                scope["scheme"] = scheme

            if host is not None:
                headers = [
                    (name, header_value)
                    for name, header_value in headers
                    if name.lower() != b"host"
                ]
                headers.append((b"host", host.encode()))
                scope["headers"] = headers
        return await super().__call__(scope, receive, send)


def _get_trusted_value(
    name: bytes,
    headers: Iterable[tuple[bytes, bytes]],
    trusted_hops: int,
) -> str | None:
    """Return the trusted value for a forwarded header.

    Args:
        name (bytes): Header name to inspect.
        headers (Iterable[tuple[bytes, bytes]]): ASGI header pairs.
        trusted_hops (int): Number of trusted proxy hops.

    Returns:
        str | None: Trusted header value when available.
    """
    if trusted_hops == 0:
        return None

    values = []
    for header_name, header_value in headers:
        if header_name.lower() == name:
            values.extend([
                value.decode("latin1").strip()
                for value in header_value.split(b",")
            ])

    if len(values) >= trusted_hops:
        return values[-trusted_hops]

    return None


__all__ = ["QuartSocketIOMiddleware"]
