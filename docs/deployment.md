# Deploy e proxies

## Runner Uvicorn

`socketio.run(app)` usa `pulseio._uvicorn.run_uvicorn()` internamente.

```python
socketio.run(app, host="0.0.0.0", port=8000, log_level="info")
```

O wrapper cria uma configuracao Uvicorn com:

- `interface="asgi3"`
- `ws="websockets"`
- `loop="asyncio"` no Windows
- `loop="uvloop"` em outros sistemas

## Middleware ASGI

Durante `init_app()`, PulseIo:

1. Cria um `socketio.AsyncServer`.
2. Registra handlers e namespaces.
3. Envolve `app.asgi_app` com `ProxyHeadersMiddleware`.
4. Instala `QuartSocketIOMiddleware` como `app.asgi_app`.
5. Salva a extensao em `app.extensions["socketio"]`.

## Headers de proxy

`QuartSocketIOMiddleware` ajusta `scope["client"]`, `scope["scheme"]` e o
header `host` quando recebe headers de proxy confiaveis.

Configuracoes lidas do `app.config`:

| Chave | Default | Descricao |
| --- | --- | --- |
| `SOCKETIO_MODE` | `modern` | Usa `Forwarded` quando disponivel. |
| `SOCKETIO_TRUSTED_HOPS` | `1` | Quantos hops da direita confiar. |

No modo `modern`, o middleware entende o header `Forwarded`:

```text
Forwarded: for=203.0.113.10;proto=https;host=example.com
```

Quando `Forwarded` nao esta disponivel, usa:

- `X-Forwarded-For`
- `X-Forwarded-Proto`
- `X-Forwarded-Host`

Use `SOCKETIO_TRUSTED_HOPS=0` para ignorar esses headers.
