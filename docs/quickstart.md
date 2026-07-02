# First app

Create a Quart application, initialize `SocketIO`, and register events with
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

## Late initialization

You can also create the extension without an app and initialize it later:

```python
from quart import Quart
from pulseio import SocketIO

socketio = SocketIO()


def create_app():
    app = Quart(__name__)
    socketio.init_app(app)
    return app
```

## Handler context

Socket.IO handlers can access the Quart context created by Quart-SocketIo during the
event. The code creates a `Request` with dynamic `sid` and `namespace`
attributes so helpers such as `emit()` and `join_room()` know which client
started the event.

```python
from pulseio import emit, join_room


@socketio.on("join")
async def join(data):
    await join_room(data["room"])
    await emit("joined", {"room": data["room"]})
```
