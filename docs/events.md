# Eventos

## `@socketio.on`

Use `on()` quando o nome do evento for explicito ou quando precisar informar
um namespace.

```python
@socketio.on("chat message", namespace="/chat")
async def handle_chat(data):
    await socketio.emit("chat message", data, namespace="/chat")
```

## `@socketio.event`

Use `event()` quando o nome do evento for o nome da funcao.

```python
@socketio.event
async def status(data):
    return {"ok": True, "data": data}
```

Equivale a:

```python
@socketio.on("status")
async def status(data):
    return {"ok": True, "data": data}
```

## Registro sem decorator

`on_event()` registra um handler diretamente.

```python
async def handle_refresh(data):
    return {"refreshed": True}


socketio.on_event("refresh", handle_refresh)
```

## Envio de eventos

`SocketIO.emit()` pode ser usado fora do contexto de um evento, por exemplo em
rotas HTTP ou tarefas de background.

```python
@app.post("/notify")
async def notify():
    await socketio.emit("notification", {"kind": "manual"})
    return {"queued": True}
```

O helper global `emit()` deve ser usado dentro de handlers Socket.IO. Ele usa
`quart.request.sid` e `quart.request.namespace` para responder ao cliente atual
quando `broadcast=False`.

```python
from pulseio import emit


@socketio.event
async def ping(data):
    await emit("pong", data)
```

## `send()` e `call()`

`send()` e uma forma simplificada de enviar uma mensagem `message` ou `json`.
`call()` emite um evento e aguarda acknowledgement do cliente ate o timeout.

```python
from pulseio import call, send


@socketio.event
async def needs_ack(data):
    result = await call("client status", data, timeout=10)
    await send({"ack": result}, json=True)
```

## Desconexao

`disconnect()` encerra a conexao do cliente atual, ou de um `sid` informado.

```python
from pulseio import disconnect


@socketio.event
async def guard(data):
    if data.get("blocked"):
        await disconnect()
```
