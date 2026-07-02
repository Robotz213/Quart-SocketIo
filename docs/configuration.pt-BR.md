# Configuração

`pulseio.Config` é um `UserDict` inicializado com uma cópia profunda dos
defaults. Isso evita que listas e dicionários mutáveis sejam compartilhados
entre instâncias.

## Defaults principais

| Opção                  | Default                    | Descrição                                             |
| ---------------------- | -------------------------- | ----------------------------------------------------- |
| `app`                  | `None`                     | Aplicação Quart associada.                            |
| `host`                 | `localhost`                | Host usado por `socketio.run()`.                      |
| `port`                 | `5000`                     | Porta usada por `socketio.run()`.                     |
| `debug`                | `False`                    | Define `app.debug`.                                   |
| `use_reloader`         | `False`                    | Opção preservada para reloader.                       |
| `launch_mode`          | `uvicorn`                  | Modo de servidor declarado.                           |
| `manage_session`       | `True`                     | Controla como sessões Quart são tratadas nos eventos. |
| `logger`               | `False`                    | Logger do python-socketio.                            |
| `engineio_logger`      | `False`                    | Logger do Engine.IO.                                  |
| `socketio_path`        | `/socket.io`               | Caminho do endpoint Socket.IO.                        |
| `engineio_path`        | `/engine.io`               | Caminho declarado do Engine.IO.                       |
| `async_mode`           | `asgi`                     | Modo async repassado ao python-socketio.              |
| `cors_allowed_origins` | `*`                        | Origens CORS aceitas.                                 |
| `cors_credentials`     | `True`                     | Permite credenciais em CORS.                          |
| `transports`           | `["polling", "websocket"]` | Transportes habilitados.                              |
| `message_queue`        | `None`                     | URL de fila para múltiplos processos.                 |
| `channel`              | `quart-socketio`           | Canal da fila.                                        |

## Opções do Socket.IO

A maior parte das opções em `Config` é repassada para
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

## Filas e múltiplos processos

Quando `message_queue` é configurado, o projeto escolhe um manager conforme o
prefixo da URL:

| Prefixo                 | Manager                      |
| ----------------------- | ---------------------------- |
| `redis://`, `rediss://` | `socketio.AsyncRedisManager` |
| `kafka://`              | `socketio.KafkaManager`      |
| `zmq`                   | `socketio.ZmqManager`        |
| Outros prefixos         | `socketio.KombuManager`      |

```python
socketio = SocketIO(
    app=app,
    message_queue="redis://localhost:6379/0",
    channel="quart-socketio",
)
```

## Sessões

Com `manage_session=True`, Quart-SocketIo cria uma sessão gerenciada para eventos
Socket.IO. Com `manage_session=False`, o código tenta usar o objeto de sessão
gerenciado pelo Quart.
