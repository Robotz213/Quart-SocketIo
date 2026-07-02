# Namespaces and rooms

## Class-based namespaces

Subclass `quart_socketio.Namespace` to group related events. Methods prefixed with
`on_` are used as handlers.

```python
from quart_socketio import Namespace


class ChatNamespace(Namespace):
    async def on_connect(self, sid, environ):
        await self.emit("ready", {"sid": sid})

    async def on_message(self, data):
        await self.emit("message", data)


socketio.on_namespace(ChatNamespace("/chat"))
```

`Namespace.emit()`, `Namespace.send()`, and `Namespace.close_room()` use the
instance namespace when no namespace is provided.

## Rooms

Rooms let you send messages to groups of clients within a namespace.

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

## Closing rooms

`close_room()` removes users from a room and deletes the room on the server.

```python
from quart_socketio import close_room


@socketio.on("close room")
async def close(data):
    await close_room(data["room"])
```
