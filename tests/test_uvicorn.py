from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

import pytest

from quart_socketio import _uvicorn
from quart_socketio.common.exceptions import QuartValueError


def test_run_uvicorn_requires_app() -> None:
    with pytest.raises(QuartValueError, match="'app'"):
        _uvicorn.run_uvicorn()  # pyright: ignore[reportCallIssue]


def test_run_uvicorn_builds_server(monkeypatch: Any) -> None:
    import uvicorn

    configs: list[dict[str, Any]] = []
    dict_configs: list[dict[str, Any]] = []

    class FakeConfig:
        def __init__(self, app: object, **kwargs: Any) -> None:
            configs.append({"app": app, **kwargs})

    @dataclass
    class FakeServer:
        config: FakeConfig

    def fake_dict_config(config: dict[str, Any]) -> None:
        dict_configs.append(config)

    monkeypatch.setattr(uvicorn, "Config", FakeConfig)
    monkeypatch.setattr(uvicorn, "Server", FakeServer)
    monkeypatch.setattr(_uvicorn, "dictConfig", fake_dict_config)
    monkeypatch.setattr(_uvicorn.platform, "system", lambda: "Linux")

    server = cast("Any", _uvicorn.run_uvicorn)(
        app=object(),
        host="127.0.0.1",
        port=9000,
        log_level="debug",
    )

    assert isinstance(server, FakeServer)
    assert configs[0]["host"] == "127.0.0.1"
    assert configs[0]["port"] == 9000
    assert configs[0]["loop"] == "uvloop"
    assert configs[0]["ws"] == "websockets"
    assert configs[0]["interface"] == "asgi3"
    assert dict_configs[0]["loggers"]["uvicorn"]["level"] == "debug"
