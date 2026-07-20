from __future__ import annotations

import platform
import ssl
from collections import UserDict
from typing import TYPE_CHECKING, TypedDict, Unpack, cast

from uvicorn.config import LOGGING_CONFIG, SSL_PROTOCOL_VERSION

from quart_socketio.common.exceptions import raise_value_error

from .constant import load_log_config

if TYPE_CHECKING:
    import asyncio
    import os
    from collections.abc import Awaitable, Callable
    from configparser import RawConfigParser
    from typing import IO, Any

    from uvicorn import Config as ConfigUvicorn
    from uvicorn import Server
    from uvicorn._types import ASGIApplication
    from uvicorn.config import (
        HTTPProtocolType,
        InterfaceType,
        LifespanType,
        LoopFactoryType,
        WSProtocolType,
    )

    from ._types._config import Config


class UvicornConfigDict(TypedDict):
    app: ASGIApplication | Callable[..., Any] | str
    host: str
    port: int
    uds: str | None
    fd: int | None
    loop: LoopFactoryType | str
    http: type[asyncio.Protocol] | HTTPProtocolType | str
    ws: type[asyncio.Protocol] | WSProtocolType | str
    ws_max_size: int
    ws_max_queue: int
    ws_ping_interval: float | None
    ws_ping_timeout: float | None
    ws_per_message_deflate: bool
    lifespan: LifespanType
    env_file: str | os.PathLike[str] | None
    log_config: (
        dict[str, Any]
        | str
        | os.PathLike[str]
        | RawConfigParser
        | IO[Any]
        | None
    )
    log_level: str | int | None
    access_log: bool
    use_colors: bool | None
    interface: InterfaceType
    reload: bool
    reload_dirs: list[str] | str | None
    reload_delay: float
    reload_includes: list[str] | str | None
    reload_excludes: list[str] | str | None
    workers: int | None
    proxy_headers: bool
    server_header: bool
    date_header: bool
    forwarded_allow_ips: list[str] | str | None
    root_path: str
    limit_concurrency: int | None
    limit_max_requests: int | None
    limit_max_requests_jitter: int
    backlog: int
    timeout_keep_alive: int
    timeout_notify: int
    timeout_graceful_shutdown: int | None
    timeout_worker_healthcheck: int
    callback_notify: Callable[..., Awaitable[None]] | None
    ssl_keyfile: str | os.PathLike[str] | None
    ssl_certfile: str | os.PathLike[str] | None
    ssl_keyfile_password: str | None
    ssl_version: int
    ssl_cert_reqs: int
    ssl_ca_certs: str | os.PathLike[str] | None
    ssl_ciphers: str | None
    ssl_context_factory: (
        Callable[[ConfigUvicorn, Callable[[], ssl.SSLContext]], ssl.SSLContext]
        | None
    )
    headers: list[tuple[str, str]] | None
    factory: bool
    h11_max_incomplete_event_size: int | None
    reset_contextvars: bool


class UvicornConfig(UserDict):
    app: ASGIApplication | Callable[..., Any] | str
    host: str = "127.0.0.1"
    port: int = 8000
    uds: str | None = None
    fd: int | None = None
    loop: LoopFactoryType | str = "auto"
    http: type[asyncio.Protocol] | HTTPProtocolType | str = "auto"
    ws: type[asyncio.Protocol] | WSProtocolType | str = "auto"
    ws_max_size: int = 16 * 1024 * 1024
    ws_max_queue: int = 32
    ws_ping_interval: float | None = 20.0
    ws_ping_timeout: float | None = 20.0
    ws_per_message_deflate: bool = True
    lifespan: LifespanType = "auto"
    env_file: str | os.PathLike[str] | None = None
    log_config: (
        dict[str, Any]
        | str
        | os.PathLike[str]
        | RawConfigParser
        | IO[Any]
        | None
    ) = LOGGING_CONFIG
    log_level: str | int | None = None
    access_log: bool = True
    use_colors: bool | None = None
    interface: InterfaceType = "auto"
    reload: bool = False
    reload_dirs: list[str] | str | None = None
    reload_delay: float = 0.25
    reload_includes: list[str] | str | None = None
    reload_excludes: list[str] | str | None = None
    workers: int | None = None
    proxy_headers: bool = True
    server_header: bool = True
    date_header: bool = True
    forwarded_allow_ips: list[str] | str | None = None
    root_path: str = ""
    limit_concurrency: int | None = None
    limit_max_requests: int | None = None
    limit_max_requests_jitter: int = 0
    backlog: int = 2048
    timeout_keep_alive: int = 5
    timeout_notify: int = 30
    timeout_graceful_shutdown: int | None = None
    timeout_worker_healthcheck: int = 5
    callback_notify: Callable[..., Awaitable[None]] | None = None
    ssl_keyfile: str | os.PathLike[str] | None = None
    ssl_certfile: str | os.PathLike[str] | None = None
    ssl_keyfile_password: str | None = None
    ssl_version: int = SSL_PROTOCOL_VERSION
    ssl_cert_reqs: int = ssl.CERT_NONE
    ssl_ca_certs: str | os.PathLike[str] | None = None
    ssl_ciphers: str | None = None
    ssl_context_factory: (
        Callable[[ConfigUvicorn, Callable[[], ssl.SSLContext]], ssl.SSLContext]
        | None
    ) = None
    headers: list[tuple[str, str]] | None = None
    factory: bool = False
    h11_max_incomplete_event_size: int | None = None
    reset_contextvars: bool = False

    def to_typed(self) -> UvicornConfigDict:
        result: dict[str, object] = {}

        for key in UvicornConfigDict.__annotations__:
            if key in self.data:
                # O valor definido na instância tem prioridade.
                result[key] = self.data[key]
            elif hasattr(type(self), key):
                # Caso contrário, usa o default declarado na classe.
                result[key] = getattr(type(self), key)
            else:
                # `app` não possui valor default.
                msg = f"O campo obrigatório {key!r} não foi definido."
                raise ValueError(msg)

        return cast("UvicornConfigDict", result)


def run_uvicorn(**kwargs: Unpack[Config]) -> Server:
    """Run Uvicorn server with the given keyword arguments.

    This function is a wrapper around `uvicorn.run`
    to allow for easy integration
    with Quart-SocketIO applications.
    """
    import uvicorn

    kw_ = UvicornConfig(kwargs).to_typed()
    log_config = kwargs.get("log_config")

    # Ensure that the 'app' keyword argument is provided
    if "app" not in kwargs:
        raise_value_error("The 'app' keyword argument must be provided.")

    if not log_config:
        cfg_ = load_log_config(**kwargs)
        kw_["log_level"] = "info"
        kw_["log_config"] = cfg_

    system_loop = "uvloop" if platform.system() == "linux" else "windows"
    loop = kwargs.get("loop", system_loop) or system_loop
    timeout_shutdown = int(kwargs.get("timeout_graceful_shutdown", 5) or 5)

    kw_["loop"] = loop
    kw_["timeout_graceful_shutdown"] = timeout_shutdown

    config = uvicorn.Config(**kw_)

    return uvicorn.Server(config)
