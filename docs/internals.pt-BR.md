# Arquitetura interna

## Visão geral

Quart-SocketIo tem três camadas principais:

1. API pública em `quart_socketio.__init__`, `SocketIO`, `Namespace` e helpers.
2. Controlador em `quart_socketio.core.Controller`, que cria o servidor Socket.IO,
   instala middleware e monta contexto Quart para eventos.
3. Middleware ASGI em `quart_socketio.middleware`, que roteia tráfego Socket.IO e
   ajusta headers de proxy antes de entregar chamadas ao app.

## Fluxo de inicialização

`SocketIO` herda de `Controller`.

```text
SocketIO(...)
  -> Controller.__init__
  -> Config(...)
  -> init_app(...) quando app ou message_queue existem
  -> configure_server()
  -> QuartSocketIOMiddleware(...)
  -> app.extensions["socketio"] = self
```

`configure_server()` cria `socketio.AsyncServer(**config)`, registra handlers
decorados, registra namespaces e substitui `_trigger_event` pelo dispatcher do
Quart-SocketIo.

## Fluxo de evento

Quando o python-socketio dispara um evento, `SocketIO._trigger_event()`:

1. Identifica `sid`, `event`, `namespace` e `environ`.
2. Guarda o environ em `self.environments` no evento `connect`.
3. Procura handler registrado por decorator.
4. Procura handler por namespace.
5. Monta kwargs padronizados com `event`, `namespace`, `sid`, `environ`,
   `data` e `handler`.
6. Chama `_handle_event()`.

`_handle_event()` cria um `Request` Quart com `make_request()` e executa o
handler dentro de `app.request_context(...)`, exceto para `disconnect`, que é
tratado diretamente.

## Estado de conexões

`SocketIO.environments` armazena o environ por `sid`.

`SocketIO.enviroments` existe como alias de compatibilidade com o typo antigo.
Não use em código novo.

## Compatibilidade com typo público

O arquivo `quart_socketio.middleare` reexporta `QuartSocketIOMiddleware` de
`quart_socketio.middleware`. Ele existe para manter imports antigos funcionando:

```python
from quart_socketio.middleare import QuartSocketIOMiddleware
```

Código novo deve importar:

```python
from quart_socketio.middleware import QuartSocketIOMiddleware
```

## Tipos internos

`quart_socketio._types` concentra aliases e `TypedDicts` usados na tipagem interna.
Eles ajudam o desenvolvimento, mas não são a API principal para usuários.
