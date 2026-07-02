# Deployment and proxies

## Uvicorn runner

`socketio.run(app)` uses `quart_socketio._uvicorn.run_uvicorn()` internally.

```python
socketio.run(app, host="0.0.0.0", port=8000, log_level="info")
```

The wrapper creates a Uvicorn configuration with:

- `interface="asgi3"`
- `ws="websockets"`
- `loop="asyncio"` on Windows
- `loop="uvloop"` on other systems

## ASGI middleware

During `init_app()`, Quart-SocketIo:

1. Creates a `socketio.AsyncServer`.
2. Registers handlers and namespaces.
3. Wraps `app.asgi_app` with `ProxyHeadersMiddleware`.
4. Installs `QuartSocketIOMiddleware` as `app.asgi_app`.
5. Stores the extension in `app.extensions["socketio"]`.

## Proxy headers

`QuartSocketIOMiddleware` adjusts `scope["client"]`, `scope["scheme"]`, and the
`host` header when it receives trusted proxy headers.

Configuration values read from `app.config`:

| Key                     | Default  | Description                             |
| ----------------------- | -------- | --------------------------------------- |
| `SOCKETIO_MODE`         | `modern` | Uses `Forwarded` when available.        |
| `SOCKETIO_TRUSTED_HOPS` | `1`      | Number of hops from the right to trust. |

In `modern` mode, the middleware understands the `Forwarded` header:

```text
Forwarded: for=203.0.113.10;proto=https;host=example.com
```

When `Forwarded` is not available, it uses:

- `X-Forwarded-For`
- `X-Forwarded-Proto`
- `X-Forwarded-Host`

Use `SOCKETIO_TRUSTED_HOPS=0` to ignore these headers.
