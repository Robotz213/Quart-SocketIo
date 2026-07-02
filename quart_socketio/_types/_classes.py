from __future__ import annotations

from collections.abc import Callable
from typing import Any

from engineio import AsyncServer as AsyncEIOServer
from socketio import AsyncServer


class SocketIo(AsyncServer, AsyncEIOServer):
    eio: AsyncEIOServer


type Function = Callable[..., Any]
