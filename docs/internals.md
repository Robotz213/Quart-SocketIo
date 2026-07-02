# Internal architecture

## Overview

Quart-SocketIo has three main layers:

1. Public API in `quart_socketio.__init__`, `SocketIO`, `Namespace`, and helpers.
2. Controller logic in `quart_socketio.core.Controller`, which creates the Socket.IO
   server, installs middleware, and builds Quart context for events.
3. ASGI middleware in `quart_socketio.middleware`, which routes Socket.IO traffic and
   adjusts proxy headers before handing calls to the app.

## Initialization flow

`SocketIO` inherits from `Controller`.

```text
SocketIO(...)
  -> Controller.__init__
  -> Config(...)
  -> init_app(...) when app or message_queue exists
  -> configure_server()
  -> QuartSocketIOMiddleware(...)
  -> app.extensions["socketio"] = self
```

`configure_server()` creates `socketio.AsyncServer(**config)`, registers
decorated handlers, registers namespaces, and replaces `_trigger_event` with
the Quart-SocketIo dispatcher.

## Event flow

When python-socketio fires an event, `SocketIO._trigger_event()`:

1. Identifies `sid`, `event`, `namespace`, and `environ`.
2. Stores the environ in `self.environments` on the `connect` event.
3. Looks for a handler registered by decorator.
4. Looks for a namespace handler.
5. Builds standardized kwargs with `event`, `namespace`, `sid`, `environ`,
   `data`, and `handler`.
6. Calls `_handle_event()`.

`_handle_event()` creates a Quart `Request` with `make_request()` and runs the
handler inside `app.request_context(...)`, except for `disconnect`, which is
handled directly.

## Connection state

`SocketIO.environments` stores the environ by `sid`.

`SocketIO.enviroments` exists as a compatibility alias for the old typo. Do
not use it in new code.

## Public typo compatibility

The `quart_socketio.middleare` file reexports `QuartSocketIOMiddleware` from
`quart_socketio.middleware`. It exists to keep old imports working:

```python
from quart_socketio.middleare import QuartSocketIOMiddleware
```

New code should import:

```python
from quart_socketio.middleware import QuartSocketIOMiddleware
```

## Internal types

`quart_socketio._types` contains aliases and `TypedDicts` used by internal typing.
They help development, but are not the main user-facing API.
