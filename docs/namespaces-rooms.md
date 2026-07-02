# Namespaces e rooms

## Namespaces por classe

Subclasse `pulseio.Namespace` para agrupar eventos relacionados. Metodos com
prefixo `on_` sao usados como handlers.

```python
from pulseio import Namespace


class ChatNamespace(Namespace):
    async def on_connect(self, sid, environ):
        await self.emit("ready", {"sid": sid})

    async def on_message(self, data):
        await self.emit("message", data)


socketio.on_namespace(ChatNamespace("/chat"))
```

`Namespace.emit()`, `Namespace.send()` e `Namespace.close_room()` usam o
namespace da instancia quando nenhum namespace e informado.

## Rooms

Rooms permitem enviar mensagens para grupos de clientes dentro de um namespace.

```python
from pulseio import emit, join_room, leave_room, rooms


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

`close_room()` remove os usuarios de uma room e apaga a room no servidor.

```python
from pulseio import close_room


@socketio.on("close room")
async def close(data):
    await close_room(data["room"])
```
