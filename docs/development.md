# Development

## Quality

Recommended commands:

```bash
uv run ruff format .
uv run ruff check .
uv run pyright
uv run pytest
```

## Documentation

The documentation uses MkDocs with Material, static i18n, and mkdocstrings.

To serve it locally:

```bash
uv run mkdocs serve
```

To generate the static site:

```bash
uv run mkdocs build --strict
```

The output is written to `site/`.

## Relevant structure

```text
quart_socketio/
  __init__.py          # public exports
  main.py              # SocketIO and event decorators
  core.py              # Controller, init_app, run, Quart context
  config.py            # configuration defaults
  namespace.py         # Namespace based on socketio.AsyncNamespace
  middleware.py        # ASGI middleware and proxy headers
  middleare.py         # compatibility shim
  _utils.py            # global context helpers
  _uvicorn.py          # Uvicorn runner wrapper
  common/exceptions.py # custom exceptions
  _types/              # internal types
```

## Existing tests

The current tests cover:

- isolation of mutable `Config` defaults;
- isolation of `SocketIO.environments`;
- custom exceptions and raise helpers;
- the `quart_socketio.middleare` shim;
- trusted header selection by hop;
- `SocketIO` handler registration, dispatching, namespaces, and delegation.

## Checklist before publishing

```bash
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv run mkdocs build --strict
uv run python -m build
```
