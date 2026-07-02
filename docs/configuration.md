# Configuracao

`pulseio.Config` e um `UserDict` inicializado com uma copia profunda dos
defaults. Isso evita que listas e dicionarios mutaveis sejam compartilhados
entre instancias.

## Defaults principais

| Opcao | Default | Descricao |
| --- | --- | --- |
| `app` | `None` | Aplicacao Quart associada. |
| `host` | `localhost` | Host usado por `socketio.run()`. |
| `port` | `5000` | Porta usada por `socketio.run()`. |
| `debug` | `False` | Define `app.debug`. |
| `use_reloader` | `False` | Opcao preservada para reloader. |
| `launch_mode` | `uvicorn` | Modo declarado de servidor. |
| `manage_session` | `True` | Controla como sessoes Quart sao tratadas nos eventos. |
| `logger` | `False` | Logger do python-socketio. |
| `engineio_logger` | `False` | Logger do engine.io. |
| `socketio_path` | `/socket.io` | Caminho do endpoint Socket.IO. |
| `engineio_path` | `/engine.io` | Caminho declarado do Engine.IO. |
| `async_mode` | `asgi` | Modo async repassado ao python-socketio. |
| `cors_allowed_origins` | `*` | Origens CORS aceitas. |
| `cors_credentials` | `True` | Permite credenciais em CORS. |
| `transports` | `["polling", "websocket"]` | Transportes habilitados. |
| `message_queue` | `None` | URL de fila para multiplos processos. |
| `channel` | `quart-socketio` | Canal da fila. |

## Opcoes do Socket.IO

A maior parte das opcoes em `Config` e repassada para
`socketio.AsyncServer(**config)`, incluindo:

- `client_manager`
- `json`
- `async_handlers`
- `always_connect`
- `namespaces`
- `ping_interval`
- `ping_timeout`
- `max_http_buffer_size`
- `allow_upgrades`
- `http_compression`
- `compression_threshold`
- `cookie`
- `monitor_clients`

## Filas e multiplos processos

Quando `message_queue` e configurado, o projeto escolhe um manager conforme o
prefixo da URL:

| Prefixo | Manager |
| --- | --- |
| `redis://`, `rediss://` | `socketio.AsyncRedisManager` |
| `kafka://` | `socketio.KafkaManager` |
| `zmq` | `socketio.ZmqManager` |
| outros | `socketio.KombuManager` |

```python
socketio = SocketIO(
    app=app,
    message_queue="redis://localhost:6379/0",
    channel="quart-socketio",
)
```

## Sessoes

Com `manage_session=True`, PulseIo cria uma sessao gerenciada para eventos
Socket.IO. Com `manage_session=False`, o codigo tenta usar o objeto de sessao
gerenciado pelo Quart.
