from quart_socketio import Config, SocketIO


def test_config_mutable_defaults_are_isolated() -> None:
    first = Config()
    second = Config()

    first["handlers"].append(("event", object(), "/"))
    first["reloader_options"]["extra_files"] = ["app.py"]
    first["server_options"]["debug"] = True

    assert second["handlers"] == []
    assert second["reloader_options"] == {}
    assert second["server_options"] == {}


def test_socketio_environments_are_isolated() -> None:
    first = SocketIO()
    second = SocketIO()

    first.environments["sid"] = {"PATH_INFO": "/socket.io"}

    assert second.environments == {}
    assert first.enviroments is first.environments
