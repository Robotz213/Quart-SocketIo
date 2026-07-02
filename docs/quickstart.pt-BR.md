# Primeiro app

Crie uma aplicação Quart, inicialize `SocketIO` e registre eventos com
decorators.

```python
from quart import Quart, render_template
from pulseio import SocketIO, emit

app = Quart(__name__)
app.config["SECRET_KEY"] = "secret!"

socketio = SocketIO(app=app)


@app.route("/")
async def index():
    return await render_template("index.html")


@socketio.event
async def my_event(data):
    await emit("my response", {"data": "got it!", "input": data})


if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=5000)
```

## Inicialização tardia

Também é possível criar a extensão sem app e inicializá-la depois:

```python
from quart import Quart
from pulseio import SocketIO

socketio = SocketIO()


def create_app():
    app = Quart(__name__)
    socketio.init_app(app)
    return app
```

## Contexto dos handlers

Handlers Socket.IO podem acessar o contexto Quart criado pelo Quart-SocketIo durante o
evento. O código cria um `Request` com `sid` e `namespace` dinâmicos para que
helpers como `emit()` e `join_room()` saibam qual cliente originou o evento.

```python
from pulseio import emit, join_room


@socketio.on("join")
async def join(data):
    await join_room(data["room"])
    await emit("joined", {"room": data["room"]})
```
