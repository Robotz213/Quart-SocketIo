# Configuration

`quart_socketio.Config` is a `UserDict` initialized with a deep copy of the defaults.
This prevents mutable lists and dictionaries from being shared across
instances.

## Main defaults

| Option                 | Default                    | Description                                            |
| ---------------------- | -------------------------- | ------------------------------------------------------ |
| `app`                  | `None`                     | Associated Quart application.                          |
| `host`                 | `localhost`                | Host used by `socketio.run()`.                         |
| `port`                 | `5000`                     | Port used by `socketio.run()`.                         |
| `debug`                | `False`                    | Sets `app.debug`.                                      |
| `use_reloader`         | `False`                    | Preserved reloader option.                             |
| `launch_mode`          | `uvicorn`                  | Declared server mode.                                  |
| `manage_session`       | `True`                     | Controls how Quart sessions are handled during events. |
| `logger`               | `False`                    | python-socketio logger.                                |
| `engineio_logger`      | `False`                    | Engine.IO logger.                                      |
| `socketio_path`        | `/socket.io`               | Socket.IO endpoint path.                               |
| `engineio_path`        | `/engine.io`               | Declared Engine.IO path.                               |
| `async_mode`           | `asgi`                     | Async mode passed to python-socketio.                  |
| `cors_allowed_origins` | `*`                        | Accepted CORS origins.                                 |
| `cors_credentials`     | `True`                     | Allows credentials in CORS.                            |
| `transports`           | `["polling", "websocket"]` | Enabled transports.                                    |
| `message_queue`        | `None`                     | Queue URL for multiple processes.                      |
| `channel`              | `quart-socketio`           | Queue channel.                                         |

## Socket.IO options

Most options in `Config` are passed to `socketio.AsyncServer(**config)`,
including:

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

## Queues and multiple processes

When `message_queue` is configured, the project selects a manager based on the
URL prefix:

| Prefix                  | Manager                      |
| ----------------------- | ---------------------------- |
| `redis://`, `rediss://` | `socketio.AsyncRedisManager` |
| `kafka://`              | `socketio.KafkaManager`      |
| `zmq`                   | `socketio.ZmqManager`        |
| Other prefixes          | `socketio.KombuManager`      |

```python
socketio = SocketIO(
    app=app,
    message_queue="redis://localhost:6379/0",
    channel="quart-socketio",
)
```

## Sessions

With `manage_session=True`, Quart-SocketIo creates a managed session for Socket.IO
events. With `manage_session=False`, the code tries to use the session object
managed by Quart.
