# Namespaces e rooms

## Namespaces por classe

Subclasse `quart_socketio.Namespace` para agrupar eventos relacionados. Métodos com
prefixo `on_` são usados como handlers.

```python
from quart_socketio import Namespace


class ChatNamespace(Namespace):
    async def on_connect(self, sid, environ):
        await self.emit("ready", {"sid": sid})

    async def on_message(self, data):
        await self.emit("message", data)


socketio.on_namespace(ChatNamespace("/chat"))
```

`Namespace.emit()`, `Namespace.send()` e `Namespace.close_room()` usam o
namespace da instância quando nenhum namespace é informado.

## Rooms

Rooms permitem enviar mensagens para grupos de clientes dentro de um namespace.

```python
from quart_socketio import emit, join_room, leave_room, rooms


@socketio.on("join", namespace="/chat")
async def join(data):
    room = data["room"]
    await join_room(room)
    await emit("system", {"event": "joined", "room": room}, to=room)


@socketio.on("leave", namespace="/chat")
async def leave(data):
    room = data["room"]
    await leave_room(room)
    await emit("system", {"event": "left", "room": room}, to=room)


@socketio.on("my rooms", namespace="/chat")
async def my_rooms(data):
    await emit("rooms", {"items": rooms()})
```

## Fechando rooms

`close_room()` remove os usuários de uma room e apaga a room no servidor.

```python
from quart_socketio import close_room


@socketio.on("close room")
async def close(data):
    await close_room(data["room"])
```
