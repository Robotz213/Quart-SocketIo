# Arquitetura interna

## Visao geral

PulseIo tem tres camadas principais:

1. API publica em `pulseio.__init__`, `SocketIO`, `Namespace` e helpers.
2. Controlador em `pulseio.core.Controller`, que cria o servidor Socket.IO,
   instala middleware e monta contexto Quart para eventos.
3. Middleware ASGI em `pulseio.middleware`, que roteia trafego Socket.IO e
   ajusta headers de proxy antes de entregar chamadas ao app.

## Fluxo de inicializacao

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
PulseIo.

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
handler dentro de `app.request_context(...)`, exceto para `disconnect`, que e
tratado diretamente.

## Estado de conexoes

`SocketIO.environments` armazena o environ por `sid`.

`SocketIO.enviroments` existe como alias de compatibilidade com o typo antigo.
Nao use em codigo novo.

## Compatibilidade com typo publico

O arquivo `pulseio.middleare` reexporta `QuartSocketIOMiddleware` de
`pulseio.middleware`. Ele existe para manter imports antigos funcionando:

```python
from pulseio.middleare import QuartSocketIOMiddleware
```

Codigo novo deve importar:

```python
from pulseio.middleware import QuartSocketIOMiddleware
```

## Tipos internos

`pulseio._types` concentra aliases e `TypedDicts` usados na tipagem interna.
Eles ajudam o desenvolvimento, mas nao sao a API principal para usuarios.
