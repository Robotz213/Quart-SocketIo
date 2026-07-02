# pulseio

Socket.IO integration for Quart applications.

> **Note:** This project is a fork of [Flask-SocketIO](https://github.com/miguelgrinberg/Flask-SocketIO), adapted to work with the [Quart](https://pgjones.gitlab.io/quart/) framework.

## Installation

You can install this package using pip:

    pip install git+https://github.com/Robotz213/Quart-SocketIo.git

For local development, use `uv`:

    uv sync --all-extras --dev
    uv run ruff format .
    uv run ruff check .
    uv run pyright
    uv run pytest
    uv run mkdocs serve

## Example

```py
from quart import Quart, render_template
from pulseio import SocketIO, emit

app = Quart(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)


@app.route("/")
async def index():
    return await render_template("index.html")


@socketio.event
async def my_event(message):
    await emit("my response", {"data": "got it!"})


if __name__ == "__main__":
    socketio.run(app)
```

## Resources

- [Quart Documentation](https://quart.palletsprojects.com/en/latest/)
- [python-socketio Documentation](https://python-socketio.readthedocs.io/)
- [PyPI](https://pypi.org/project/quart-socketio/)
