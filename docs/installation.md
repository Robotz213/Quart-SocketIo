# Installation

## As a dependency

Until the package is published to PyPI, install it directly from the
repository:

```bash
pip install git+https://github.com/Robotz213/Quart-SocketIo.git
```

The project declares support for Python `>=3.13`.

## Development environment

The repository uses `uv` to resolve dependencies:

```bash
uv sync --all-extras --dev
```

After that, the maintenance commands are available:

```bash
uv run ruff format .
uv run ruff check .
uv run pyright
uv run pytest
uv run mkdocs build --strict
```

## Runtime dependencies

Quart-SocketIo depends on:

- `quart`
- `python-socketio`
- `uvicorn`
- `hypercorn`
- `websockets`
- `clear`

The runner implemented in the code uses Uvicorn by default.
