# Events

## `@socketio.on`

Use `on()` when the event name is explicit or when you need to set a
namespace.

```python
@socketio.on("chat message", namespace="/chat")
async def handle_chat(data):
    await socketio.emit("chat message", data, namespace="/chat")
```

## `@socketio.event`

Use `event()` when the event name should match the function name.

```python
@socketio.event
async def status(data):
    return {"ok": True, "data": data}
```

This is equivalent to:

```python
@socketio.on("status")
async def status(data):
    return {"ok": True, "data": data}
```

## Registration without decorator syntax

`on_event()` registers a handler directly.

```python
async def handle_refresh(data):
    return {"refreshed": True}


socketio.on_event("refresh", handle_refresh)
```

## Emitting events

`SocketIO.emit()` can be used outside an event context, for example in HTTP
routes or background tasks.

```python
@app.post("/notify")
async def notify():
    await socketio.emit("notification", {"kind": "manual"})
    return {"queued": True}
```

The global `emit()` helper should be used inside Socket.IO handlers. It uses
`quart.request.sid` and `quart.request.namespace` to reply to the current
client when `broadcast=False`.

```python
from quart_socketio import emit


@socketio.event
async def ping(data):
    await emit("pong", data)
```

## `send()` and `call()`

`send()` is a simplified way to send a `message` or `json` event. `call()`
emits an event and waits for a client acknowledgement until the timeout.

```python
from quart_socketio import call, send


@socketio.event
async def needs_ack(data):
    result = await call("client status", data, timeout=10)
    await send({"ack": result}, json=True)
```

## Disconnection

`disconnect()` closes the current client connection, or the connection for a
provided `sid`.

```python
from quart_socketio import disconnect


@socketio.event
async def guard(data):
    if data.get("blocked"):
        await disconnect()
```
