# Quart-SocketIo

Quart-SocketIo é inspirado no projeto
[Flask-SocketIO](https://github.com/miguelgrinberg/Flask-SocketIO), criado e
mantido por [Miguel Grinberg](https://github.com/miguelgrinberg). A proposta
deste projeto é trazer uma experiência semelhante para aplicações Quart
assíncronas.

Quart-SocketIo integra [Quart](https://quart.palletsprojects.com/) com
[python-socketio](https://python-socketio.readthedocs.io/) para criar
aplicações Socket.IO assíncronas em ASGI.

O pacote fornece uma API familiar para quem conhece Flask-SocketIO, mas roda
com `async`/`await`, usa Quart como aplicação web e encapsula o servidor
Socket.IO em um middleware ASGI.

## O que existe no projeto

- `quart_socketio.SocketIO`: extensão principal que registra eventos, namespaces,
  middleware e servidor ASGI.
- Helpers de contexto: `emit`, `send`, `call`, `join_room`, `leave_room`,
  `close_room`, `rooms` e `disconnect`.
- `quart_socketio.Namespace`: base para organizar namespaces por classe.
- `quart_socketio.Config`: defaults e opções de configuração do servidor.
- `quart_socketio.middleware.QuartSocketIOMiddleware`: middleware ASGI que integra
  Quart, Socket.IO e headers de proxy.
- Exceções customizadas em `quart_socketio.common.exceptions`.
- Tipos auxiliares em `quart_socketio._types`.

## Exemplo mínimo

```python
from quart import Quart
from quart_socketio import SocketIO, emit

app = Quart(__name__)
socketio = SocketIO(app=app)


@socketio.event
async def ping(data):
    await emit("pong", {"received": data})


if __name__ == "__main__":
    socketio.run(app)
```

## Comandos principais

```bash
uv sync --all-extras --dev
uv run mkdocs serve
uv run mkdocs build --strict
uv run pytest
uv run ruff check .
uv run pyright
```
