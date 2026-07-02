# Deploy e proxies

## Runner Uvicorn

`socketio.run(app)` usa `quart_socketio._uvicorn.run_uvicorn()` internamente.

```python
socketio.run(app, host="0.0.0.0", port=8000, log_level="info")
```

O wrapper cria uma configuração Uvicorn com:

- `interface="asgi3"`
- `ws="websockets"`
- `loop="asyncio"` no Windows
- `loop="uvloop"` em outros sistemas

## Middleware ASGI

Durante `init_app()`, Quart-SocketIo:

1. Cria um `socketio.AsyncServer`.
2. Registra handlers e namespaces.
3. Envolve `app.asgi_app` com `ProxyHeadersMiddleware`.
4. Instala `QuartSocketIOMiddleware` como `app.asgi_app`.
5. Salva a extensão em `app.extensions["socketio"]`.

## Headers de proxy

`QuartSocketIOMiddleware` ajusta `scope["client"]`, `scope["scheme"]` e o
header `host` quando recebe headers de proxy confiáveis.

Configurações lidas de `app.config`:

| Chave                   | Default  | Descrição                                    |
| ----------------------- | -------- | -------------------------------------------- |
| `SOCKETIO_MODE`         | `modern` | Usa `Forwarded` quando disponível.           |
| `SOCKETIO_TRUSTED_HOPS` | `1`      | Quantos hops da direita devem ser confiados. |

No modo `modern`, o middleware entende o header `Forwarded`:

```text
Forwarded: for=203.0.113.10;proto=https;host=example.com
```

Quando `Forwarded` não está disponível, usa:

- `X-Forwarded-For`
- `X-Forwarded-Proto`
- `X-Forwarded-Host`

Use `SOCKETIO_TRUSTED_HOPS=0` para ignorar esses headers.
