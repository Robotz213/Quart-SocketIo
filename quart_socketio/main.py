from __future__ import annotations

# pyright: reportAttributeAccessIssue=false
import traceback
from functools import wraps
from inspect import iscoroutinefunction
from typing import TYPE_CHECKING, Any, cast

from quart import Quart, has_request_context
from quart import websocket as request
from socketio.exceptions import (
    ConnectionRefusedError as SocketIOConnectionRefusedError,
)

from quart_socketio.common.exceptions import QuartTypeError, raise_value_error
from quart_socketio.core import Controller

from .namespace import Namespace

if TYPE_CHECKING:
    from collections.abc import Callable

    from werkzeug.datastructures.headers import Headers

    from quart_socketio._types import Function


class Reason:
    """Disconnection reasons."""

    #: Server-initiated disconnection.
    SERVER_DISCONNECT = "server disconnect"
    #: Client-initiated disconnection.
    CLIENT_DISCONNECT = "client disconnect"
    #: Ping timeout.
    PING_TIMEOUT = "ping timeout"
    #: Transport close.
    TRANSPORT_CLOSE = "transport close"
    #: Transport error.
    TRANSPORT_ERROR = "transport error"


class SocketIO(Controller):
    reason: type[Reason] = Reason

    def __init__(self, **kwargs: Any) -> None:
        self.environments: dict[str, dict[str, Any]] = {}
        self.enviroments = self.environments
        super().__init__(**kwargs)

    async def _trigger_event(  # noqa: C901
        self,
        *args: Any | int | bool | dict[str, Any],
        **kwargs: Any | int | bool | dict[str, Any],
    ) -> Any:
        """Dispatch an event to the proper handler method.

        In the most common usage, this method is not overloaded by subclasses,
        as it performs the routing of events to methods. However, this
        method can be overridden if special dispatching rules are needed, or if
        having a single method that catches all events is desired.
        """
        sid = str(args[2])
        event = str(args[0] if len(args) > 1 and args[0] != "*" else sid)
        namespace = str(args[1] if len(args) > 2 and args[1] != "*" else sid)
        environ = cast("dict[str, Any]", args[3] if len(args) > 3 else {})

        if event == "connect":
            self.environments[sid] = environ

        else:
            if isinstance(environ, dict):
                kwargs.update(environ)

        handler = self.get_handler(event=event, namespace=namespace)
        namespace_handler = self.get_namespace_handler(namespace)

        if handler:
            environ = self.get_environ(args=args, namespace=namespace, sid=sid)
            kwrg = self._update_kwargs(
                sid=sid,
                event=event,
                handler=handler,
                namespace=namespace,
                environ=environ,
                args=args,
                kwargs=kwargs,
            )
            if len(args) > 0:
                for item in args:
                    if isinstance(item, str) and getattr(
                        self.reason,
                        item.replace(" ", "_").upper(),
                        None,
                    ):
                        kwrg.update({"reason": item})
                        break

            try:
                if iscoroutinefunction(handler):
                    return await handler(**kwrg)

                return handler(**kwrg)

            except TypeError as err:
                if event != "disconnect":
                    raise QuartTypeError(
                        message=(
                            f"Handler for event '{event}' in namespace '{namespace}' "  # noqa: E501
                            "must accept at least one argument, the sid of the client"  # noqa: E501
                        ),
                    ) from err

                return await handler(**kwrg)

        elif namespace_handler:
            environ = self.get_environ(args=args, namespace=namespace, sid=sid)
            kwrg = self._update_kwargs(
                sid=sid,
                handler=handler,
                event=event,
                namespace=namespace,
                environ=environ,
                args=args,
                kwargs=kwargs,
            )
            return await namespace_handler.trigger_event(**kwrg)

        return self.server.not_handled

    async def _handle_event(
        self,
        event: str,
        namespace: str | None,
        sid: str | None,
        data: dict[str, Any],
        handler: Callable[..., Any],
        environ: dict[str, Any] | None = None,
    ) -> Any:
        app: Quart = self.sockio_mw.quart_app
        if event == "disconnect":
            try:
                if iscoroutinefunction(handler):
                    return await handler(**data)

                return handler(**data)

            except SocketIOConnectionRefusedError:
                raise  # let this error bubble up to python-socketio
            except Exception as e:  # noqa: BLE001
                err_more = "".join(traceback.format_exception(e))
                err = "".join(traceback.format_exception_only(e))
                self.config["app"].logger.error(err)
                return err

        request_ctx_sio = await self.make_request(
            environ=environ,
            sid=sid,
            namespace=namespace,
        )
        async with app.request_context(request_ctx_sio):
            if not self.config["manage_session"]:
                await self.handle_session(environ or {})

            try:
                if iscoroutinefunction(handler):
                    return await handler(**data)

                return handler(**data)

            except SocketIOConnectionRefusedError:
                raise  # let this error bubble up to python-socketio
            except Exception as e:  # noqa: BLE001
                err_more = "".join(traceback.format_exception(e))  # noqa: F841
                err = "".join(traceback.format_exception_only(e))
                self.config["app"].logger.error(err)
                return err

    def on(
        self,
        event: str,
        namespace: str = "/",
    ) -> Callable[[Function], Function]:
        """Register a SocketIO event handler.

        This decorator must be applied to SocketIO event handlers. Example::

            @socketio.on("my event", namespace="/chat")
            async def handle_my_custom_event(json):
                print("received json: " + str(json))

        :param event: The name of the event. This is normally a user defined
                        string, but a few event names are already defined. Use
                        ``'message'`` to define a handler that takes a string
                        payload, ``'json'`` to define a handler that takes a
                        JSON blob payload, ``'connect'`` or ``'disconnect'``
                        to create handlers for connection and disconnection
                        events.
        :param namespace: The namespace on which the handler is to be
                          registered. Defaults to the global namespace.

        """

        def decorator(handler: Function) -> Function:
            @wraps(handler)
            async def _handler(
                **kwargs: Any,
            ) -> Any:
                """Process the event."""
                kwargs = kwargs.copy()
                kwargs.update({"handler": handler})
                try:
                    return await self._handle_event(**kwargs)
                except TypeError as err:
                    if event != "disconnect":
                        raise QuartTypeError(
                            message=(
                                f"Handler for event '{event}' in namespace '{namespace}' "  # noqa: E501
                                f"must accept at least one argument, the sid of the client"  # noqa: E501
                            ),
                        ) from err

                    return await self._handle_event(**kwargs)

            self.config["handlers"].append((event, _handler, namespace))
            return handler

        return decorator

    def event(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Register an event handler.

        This is a simplified version of the ``on()`` method that takes the
        event name from the decorated function.

        Example usage::

            @socketio.event
            def my_event(data):
                print("Received data: ", data)

        The above example is equivalent to::

            @socketio.on("my_event")
            def my_event(data):
                print("Received data: ", data)

        A custom namespace can be given as an argument to the decorator::

            @socketio.event(namespace="/test")
            def my_event(data):
                print("Received data: ", data)

        """
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            # the decorator was invoked without arguments
            # args[0] is the decorated function
            return self.on(args[0].__name__)(args[0])
        # the decorator was invoked with arguments

        def set_handler(handler: Callable[..., Any]) -> Callable[..., Any]:
            return self.on(handler.__name__, *args, **kwargs)(handler)

        return set_handler

    def get_handler(
        self,
        event: str,
        namespace: str,
    ) -> Callable[..., Any] | None:
        filter_ = list(
            filter(
                lambda x: x[0] == event and x[2] == namespace,
                self.config["handlers"],
            ),
        )
        return filter_[0][1] if len(filter_) > 0 else None

    def get_namespace_handler(self, namespace: str) -> Namespace | None:

        handler = None
        if namespace in self.server.namespace_handlers:
            return self.server.namespace_handlers.get(namespace)

        return handler

    def get_environ(
        self,
        args: tuple[Any],
        sid: str,
        namespace: str,
    ) -> dict[str, Any]:

        return (
            self.environments.get(
                sid,
                self.server.get_environ(sid, namespace),
            )
            or {}
        )

    def _update_kwargs(
        self,
        sid: str,
        event: str,
        handler: Callable,
        namespace: str,
        environ: dict[str, Any],
        args: tuple[Any],
        kwargs: dict[str, Any],
    ) -> dict[str, Any]:

        ignore_data = [sid, event, namespace, environ, handler]
        data: dict[str, Any] = {}
        for x in args:
            if all(
                (
                    not any(x == item for item in ignore_data),
                    isinstance(x, dict),
                ),
            ):
                data.update({
                    k: v
                    for k, v in list(x.items())
                    if isinstance(x, dict) and k not in ignore_data
                })

        kwrg = kwargs.copy()
        kwrg.update({
            "event": event,
            "namespace": namespace,
            "sid": sid,
            "environ": environ,
            "data": {},
            "handler": handler,
        })

        if data:
            kwrg["data"] = data
        return kwrg

    def on_namespace(self, namespace_handler: Namespace) -> None:
        """Register a custom namespace handler.

        Args:
            namespace_handler (Namespace): The namespace handler instance to register.

        Raises:
            ValueError: If the provided handler is not an instance of Namespace.

        """  # noqa: E501
        if not isinstance(namespace_handler, Namespace):
            raise_value_error("Not a namespace instance.")

        namespace_handler.set_socketio(self)
        self.register_namespace(namespace_handler)

    def on_error(
        self,
        namespace: str = "/",
    ) -> Callable[[Function], Function]:
        """Define a custom error handler for SocketIO events.

        This decorator can be applied to a function that acts as an error
        handler for a namespace. This handler will be invoked when a SocketIO
        event handler raises an exception. The handler function must accept one
        argument, which is the exception raised. Example::

            @socketio.on_error(namespace="/chat")
            def chat_error_handler(e):
                print("An error has occurred: " + str(e))

        :param namespace: The namespace for which to register the error
                          handler. Defaults to the global namespace.
        """

        def decorator(exception_handler: Function) -> Function:
            if not callable(exception_handler):
                raise_value_error("exception_handler must be callable")
            self.config["exception_handlers"][namespace] = exception_handler
            return exception_handler

        return decorator

    def on_error_default(
        self,
        exception_handler: Function,
    ) -> Function:
        """Define a default error handler for SocketIO events.

        This decorator can be applied to a function that acts as a default
        error handler for any namespaces that do not have a specific handler.
        Example::

            @socketio.on_error_default
            def error_handler(e):
                print("An error has occurred: " + str(e))
        """
        if not callable(exception_handler):
            raise_value_error("exception_handler must be callable")

        self.config["default_exception_handler"] = exception_handler
        return exception_handler

    def on_event(
        self,
        event: str,
        handler: Callable[..., Any],
        namespace: str = "/",
    ) -> None:
        """Register a SocketIO event handler.

        ``on_event`` is the non-decorator version of ``'on'``.

        Example::

            def on_foo_event(json):
                print("received json: " + str(json))


            socketio.on_event("my event", on_foo_event, namespace="/chat")

        :param event: The name of the event. This is normally a user defined
                      string, but a few event names are already defined. Use
                      ``'message'`` to define a handler that takes a string
                      payload, ``'json'`` to define a handler that takes a JSON
                      blob payload, ``'connect'`` or ``'disconnect'`` to create
                      handlers for connection and disconnection events.
        :param handler: The function that handles the event.
        :param namespace: The namespace on which the handler is to be
                          registered. Defaults to the global namespace.
        """
        self.on(event=event, namespace=namespace)(handler)

    async def emit(
        self,
        event: str,
        data: Any | None = None,
        *args: Any,
        to: Any | None = None,
        room: Any | None = None,
        include_self: bool = True,
        skip_sid: Any | None = None,
        namespace: Any | None = None,
        callback: Callable[..., Any] | None = None,
        ignore_queue: bool = False,
        **kwargs: Any,
    ) -> None:
        """Emit a server generated SocketIO event.

        This function emits a SocketIO event to one or more connected clients.
        A JSON blob can be attached to the event as payload. This function can
        be used outside of a SocketIO event context, so it is appropriate to
        use when the server is the originator of an event, outside of any
        client context, such as in a regular HTTP request handler or a
        background task. Example::

            @app.route("/ping")
            def ping():
                socketio.emit("ping event", {"data": 42}, namespace="/chat")

        :param event: The name of the user event to emit.
        :param args: A dictionary with the JSON data to send as payload.
        :param namespace: The namespace under which the message is to be sent.
                          Defaults to the global namespace.
        :param to: Send the message to all the users in the given room, or to
                   the user with the given session ID. If this parameter is not
                   included, the event is sent to all connected users.
        :param include_self: ``True`` to include the sender when broadcasting
                             or addressing a room, or ``False`` to send to
                             everyone but the sender.
        :param skip_sid: The session id of a client to ignore when broadcasting
                         or addressing a room. This is typically set to the
                         originator of the message, so that everyone except
                         that client receive the message. To skip multiple sids
                         pass a list.
        :param callback: If given, this function will be called to acknowledge
                         that the client has received the message. The
                         arguments that will be passed to the function are
                         those provided by the client. Callback functions can
                         only be used when addressing an individual client.
        """
        if not include_self and not skip_sid:
            skip_sid = request.sid

        if callback:
            # wrap the callback so that it sets app app and request contexts
            sid = None
            original_callback = callback
            if has_request_context():
                sid = getattr(request, "sid", None)

            async def _callback_wrapper(
                *args: Any,
                **kwargs: Any,
            ) -> Any:
                if iscoroutinefunction(original_callback):
                    return await original_callback(*args, **kwargs)

                return original_callback(*args, **kwargs)

            if sid:
                # the callback wrapper above will install a request context
                # before invoking the original callback
                # we only use it if the emit was issued from a Socket.IO
                # populated request context (i.e. request.sid is defined)
                callback = _callback_wrapper
        await self.server.emit(
            event=event,
            data=data,
            to=to,
            room=room,
            skip_sid=skip_sid,
            namespace=namespace,
            callback=callback,
            ignore_queue=ignore_queue,
        )

    async def call(
        self,
        event: str,
        *args: Any,
        namespace: str = "/",
        to: Any | None = None,
        room: Any | None = None,
        timeout: int = 60,  # noqa: ASYNC109
        ignore_queue: bool = False,
        **kwargs: Any,
    ) -> Any:
        """Emit a SocketIO event and wait for the response.

        This method issues an emit with a callback and waits for the callback
        to be invoked by the client before returning. If the callback isn’t
        invoked before the timeout, then a TimeoutError exception is raised. If
        the Socket.IO connection drops during the wait, this method still waits
        until the specified timeout. Example::

            def get_status(client, data):
                status = call("status", {"data": data}, to=client)

        :param event: The name of the user event to emit.
        :param args: A dictionary with the JSON data to send as payload.
        :param namespace: The namespace under which the message is to be sent.
                          Defaults to the global namespace.
        :param to: The session ID of the recipient client.
        :param timeout: The waiting timeout. If the timeout is reached before
                        the client acknowledges the event, then a
                        ``TimeoutError`` exception is raised. The default is 60
                        seconds.
        :param ignore_queue: Only used when a message queue is configured. If
                             set to ``True``, the event is emitted to the
                             client directly, without going through the queue.
                             This is more efficient, but only works when a
                             single server process is used, or when there is a
                             single addressee. It is recommended to always
                             leave this parameter with its default value of
                             ``False``.
        """  # noqa: RUF002
        to = to or room
        return await self.server.call(
            event,
            *args,
            namespace=namespace,
            to=to,
            timeout=timeout,
            ignore_queue=ignore_queue,
            **kwargs,
        )

    async def send(
        self,
        *args: Any,
        data: Any,
        json: bool = False,
        namespace: str | None = None,
        to: str | None = None,
        callback: Callable[..., Any] | None = None,
        include_self: bool = True,
        skip_sid: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Send a server-generated SocketIO message.

        This function sends a simple SocketIO message to one or more connected
        clients. The message can be a string or a JSON blob. This is a simpler
        version of ``emit()``, which should be preferred. This function can be
        used outside of a SocketIO event context, so it is appropriate to use
        when the server is the originator of an event.

        :param data: The message to send, either a string or a JSON blob.
        :param json: ``True`` if ``message`` is a JSON blob, ``False``
                     otherwise.
        :param namespace: The namespace under which the message is to be sent.
                          Defaults to the global namespace.
        :param to: Send the message to all the users in the given room, or to
                   the user with the given session ID. If this parameter is not
                   included, the event is sent to all connected users.
        :param include_self: ``True`` to include the sender when broadcasting
                             or addressing a room, or ``False`` to send to
                             everyone but the sender.
        :param skip_sid: The session id of a client to ignore when broadcasting
                         or addressing a room. This is typically set to the
                         originator of the message, so that everyone except
                         that client receive the message. To skip multiple sids
                         pass a list.
        :param callback: If given, this function will be called to acknowledge
                         that the client has received the message. The
                         arguments that will be passed to the function are
                         those provided by the client. Callback functions can
                         only be used when addressing an individual client.
        """
        skip_sid = request.sid if not include_self else skip_sid
        if json:
            await self.emit(
                "json",
                data,
                namespace=namespace,
                to=to,
                skip_sid=skip_sid,
                callback=callback,
                **kwargs,
            )
        else:
            await self.emit(
                "message",
                data,
                namespace=namespace,
                to=to,
                skip_sid=skip_sid,
                callback=callback,
                **kwargs,
            )

    async def close_room(
        self,
        room: str,
        namespace: str | None = None,
    ) -> None:
        """Close a room.

        This function removes any users that are in the given room and then
        deletes the room from the server. This function can be used outside
        of a SocketIO event context.

        :param room: The name of the room to close.
        :param namespace: The namespace under which the room exists. Defaults
                          to the global namespace.
        """
        await self.server.close_room(room, namespace)

    def start_background_task(
        self,
        target: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Start a background task using the appropriate async model.

        This is a utility function that applications can use to start a
        background task using the method that is compatible with the
        selected async mode.

        :param target: the target function to execute.
        :param args: arguments to pass to the function.
        :param kwargs: keyword arguments to pass to the function.

        This function returns an object that represents the background task,
        on which the ``join()`` method can be invoked to wait for the task to
        complete.
        """
        return self.server.start_background_task(target, *args, **kwargs)

    def sleep(self, seconds: float = 0) -> Any:
        """Sleep for the requested amount of time using the appropriate async model.

        This is a utility function that applications can use to put a task to
        sleep without having to worry about using the correct call for the
        selected async mode.

        """  # noqa: E501
        return self.server.sleep(seconds)

    async def send_push_promise(self, data: str, headers: Headers) -> None:
        """Empty."""
        # This method is not used in the current implementation.
        # It is a placeholder for future use if push promises are implemented.
        # The headers parameter is expected to be a werkzeug Headers object.
        # Currently, it does nothing and can be safely ignored.
        pass  # noqa: PIE790
