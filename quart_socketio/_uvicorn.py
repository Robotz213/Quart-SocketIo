from __future__ import annotations

import logging
import platform
from logging.config import dictConfig
from typing import TYPE_CHECKING, Unpack

from quart_socketio.common.exceptions import raise_value_error

if TYPE_CHECKING:
    from uvicorn import Server

    from ._types._config import Config

ACCESS_FMT = (
    '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
)


def run_uvicorn(**kwargs: Unpack[Config]) -> Server:
    """Run Uvicorn server with the given keyword arguments.

    This function is a wrapper around `uvicorn.run`
    to allow for easy integration
    with Quart-SocketIO applications.
    """
    import uvicorn

    # Ensure that the 'app' keyword argument is provided
    if "app" not in kwargs:
        raise_value_error("The 'app' keyword argument must be provided.")

    app = kwargs["app"]
    log_config = kwargs.get("log_config")
    log_level = kwargs.get("log_level", "info")
    host = kwargs.get("host", "0.0.0.0")  # noqa: S104
    port = kwargs.get("port", 7000)

    if not log_config:
        log_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "()": "uvicorn.logging.DefaultFormatter",
                    "fmt": "%(levelprefix)s %(asctime)s %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
                "access": {
                    "()": "uvicorn.logging.AccessFormatter",
                    "fmt": ACCESS_FMT,
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
                "access": {
                    "formatter": "access",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "loggers": {
                "uvicorn": {"handlers": ["default"], "level": log_level},
                "uvicorn.error": {
                    "handlers": ["default"],
                    "level": log_level,
                    "propagate": False,
                },
                "uvicorn.access": {
                    "handlers": ["access"],
                    "level": log_level,
                    "propagate": False,
                },
                "uvicorn.asgi": {
                    "handlers": ["default"],
                    "level": log_level,
                    "propagate": False,
                },
                "uvicorn.lifespan": {
                    "handlers": ["default"],
                    "level": log_level,
                    "propagate": False,
                },
            },
        }
        dictConfig(log_config)

    system_loop = "uvloop" if platform.system() == "linux" else "windows"
    loop = kwargs.get("loop", system_loop) or system_loop

    timeout_shutdown = int(kwargs.get("timeout_graceful_shutdown", 5) or 5)
    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        access_log=True,
        log_config=log_config,
        log_level=logging.INFO,
        loop=loop,
        ws="websockets",
        interface="asgi3",
        timeout_graceful_shutdown=timeout_shutdown,
    )

    return uvicorn.Server(config)
