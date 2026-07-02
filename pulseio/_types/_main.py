from __future__ import annotations

from collections.abc import Callable
from typing import Any as PyAny
from typing import Literal

from socketio import AsyncRedisManager, KafkaManager, KombuManager, ZmqManager

type AsyncMode = Literal["aiohttp", "sanic", "tornado", "asgi"]
type Transports = list[Literal["polling", "websocket"]]
type LaunchMode = Literal["uvicorn", "hypercorn"]
type Any = PyAny


type Kw[T] = str | bool | Any | T
type CorsAllowOrigin = str | list[str] | Callable[[], bool] | None
type RedisURLPrefix = tuple[Literal["redis://", "rediss://"]]
type KafkaURLPrefix = tuple[Literal["kafka://"]]
type ZmqURLPrefix = tuple[Literal["zmq"]]
type TupleLiteral = tuple[RedisURLPrefix, KafkaURLPrefix, ZmqURLPrefix]
type QueueClasses = type[
    AsyncRedisManager | KafkaManager | ZmqManager | KombuManager
]
type HypercornServer = object
type QueueClassMap = dict[TupleLiteral, QueueClasses]
type TExceptionHandler = Callable[..., Any]
type Channel = Literal["quart-socketio"]

__all__ = [
    "Any",
    "AsyncMode",
    "Channel",
    "CorsAllowOrigin",
    "Kw",
    "LaunchMode",
    "QueueClassMap",
    "QueueClasses",
    "TExceptionHandler",
    "Transports",
]
