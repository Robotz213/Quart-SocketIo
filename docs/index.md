# PulseIo

PulseIo is inspired by
[Flask-SocketIO](https://github.com/miguelgrinberg/Flask-SocketIO), created
and maintained by [Miguel Grinberg](https://github.com/miguelgrinberg). This
project brings a similar developer experience to asynchronous Quart
applications.

PulseIo integrates [Quart](https://quart.palletsprojects.com/) with
[python-socketio](https://python-socketio.readthedocs.io/) to build
asynchronous Socket.IO applications on ASGI.

The package provides an API that feels familiar to Flask-SocketIO users, while
running with `async`/`await`, using Quart as the web application, and wrapping
the Socket.IO server in ASGI middleware.

## What is in the project

- `pulseio.SocketIO`: the main extension that registers events, namespaces,
  middleware, and the ASGI server.
- Context helpers: `emit`, `send`, `call`, `join_room`, `leave_room`,
  `close_room`, `rooms`, and `disconnect`.
- `pulseio.Namespace`: a base class for class-based namespaces.
- `pulseio.Config`: configuration defaults and server options.
- `pulseio.middleware.QuartSocketIOMiddleware`: ASGI middleware that connects
  Quart, Socket.IO, and proxy headers.
- Custom exceptions in `pulseio.common.exceptions`.
- Helper types in `pulseio._types`.

## Minimal example

```python
from quart import Quart
from pulseio import SocketIO, emit

app = Quart(__name__)
socketio = SocketIO(app=app)


@socketio.event
async def ping(data):
    await emit("pong", {"received": data})


if __name__ == "__main__":
    socketio.run(app)
```

## Main commands

```bash
uv sync --all-extras --dev
uv run mkdocs serve
uv run mkdocs build --strict
uv run pytest
uv run ruff check .
uv run pyright
```
