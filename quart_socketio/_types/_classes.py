from __future__ import annotations

from collections.abc import Callable
from typing import Any

from engineio import AsyncServer as AsyncEIOServer
from socketio import AsyncServer


class SocketIo(AsyncServer, AsyncEIOServer):
    """Describe the combined Socket.IO and Engine.IO server type."""

    eio: AsyncEIOServer


type Function = Callable[..., Any]
