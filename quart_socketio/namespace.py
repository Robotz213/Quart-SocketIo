from __future__ import annotations

import traceback
from inspect import iscoroutinefunction
from typing import TYPE_CHECKING, Any, cast

from socketio import AsyncNamespace as BaseNamespace
from socketio import AsyncServer
from socketio.exceptions import (
    ConnectionRefusedError as SocketIOConnectionRefusedError,
)

from quart_socketio.common.exceptions import QuartSocketioError

if TYPE_CHECKING:
    from collections.abc import Callable

    from flask.sessions import SessionMixin
    from quart import Quart, Request

    from quart_socketio import SocketIO
    from quart_socketio._types import Function


class Namespace(BaseNamespace):
    """Provide a Quart-aware asynchronous Socket.IO namespace."""

    def __init__(
        self,
        namespace: str | None = None,
        socketio: SocketIO | None = None,
    ) -> None:
        """Create a namespace bound to an optional SocketIO instance.

        Args:
            namespace (str | None): Namespace path.
            socketio (SocketIO | None): SocketIO extension instance.
        """
        super().__init__(namespace)
        self.socketio = cast("SocketIO", socketio)

    def is_asyncio_based(self) -> bool:
        """Check if the namespace is asyncio-based."""
        return True

    async def make_request(self, **kwargs: Any) -> Request:
        """Create a request dictionary for the namespace."""
        return await self.socketio.make_request(**kwargs)

    async def make_websocket(self, **kwargs: Any) -> Request:
        """Create a websocket dictionary for the namespace."""
        return await self.socketio.make_websocket(**kwargs)  # pyright: ignore[reportReturnType]

    async def trigger_event(
        self,
        sid: str,
        event: str,
        namespace: str,
        environ: dict[str, Any],
        data: dict[str, Any],
        **kwargs: Any,
    ) -> Any:
        """Dispatch an event to the proper handler method.

        In the most common usage, this method is not overloaded by subclasses,
        as it performs the routing of events to methods. However, this
        method can be overridden if special dispatching rules are needed, or if
        having a single method that catches all events is desired.
        """
        handler = self.get_handler(event=event)
        if handler:
            try:
                return await self._handle_event(
                    handler=handler,
                    sid=sid,
                    event=event,
                    namespace=namespace,
                    environ=environ,
                    data=data,
                )

            except TypeError as err:
                if event != "disconnect":
                    raise QuartSocketioError(err) from err

                return await self._handle_event(
                    handler=handler,
                    sid=sid,
                    event=event,
                    namespace=namespace,
                    environ=environ,
                    data=data,
                )

            except Exception as e:
                err_more = "".join(traceback.format_exception(e))  # noqa: F841
                err = "".join(traceback.format_exception_only(e))
                self.socketio.app.logger.exception(err)
                return err

        return self.server.not_handled

    async def _handle_event(
        self,
        data: dict[str, Any],
        event: str,
        namespace: str | None,
        sid: str | None,
        environ: dict[str, Any] | None = None,
        handler: Callable[..., Any] | None = None,
    ) -> Any:
        """Run a namespace event handler in the Quart context.

        Args:
            data (dict[str, Any]): Handler keyword arguments.
            event (str): Socket.IO event name.
            namespace (str | None): Socket.IO namespace.
            sid (str | None): Socket.IO session ID.
            environ (dict[str, Any] | None): Socket.IO environment.
            handler (Callable[..., Any] | None): Handler to execute.

        Returns:
            Any: Handler result, error string, or None.
        """

        if not handler:
            return None

        app: Quart = self.sockio_mw.quart_app
        if event == "disconnect":
            try:
                if iscoroutinefunction(handler):
                    return await handler(**data)  # pyright: ignore[reportCallIssue]

                return handler(**data)  # pyright: ignore[reportCallIssue]

            except SocketIOConnectionRefusedError:
                raise  # let this error bubble up to python-socketio
            except Exception as e:
                err_more = "".join(traceback.format_exception(e))
                err = "".join(traceback.format_exception_only(e))
                app.logger.exception(err)
                return err

        request_ctx_sio = await self.make_request(
            environ=environ,
            sid=sid,
            namespace=namespace,
        )
        async with app.request_context(request_ctx_sio):
            if not self.socketio.config["manage_session"]:
                await self.socketio.handle_session(environ or {})

            try:
                if iscoroutinefunction(handler):
                    return await handler(**data)  # pyright: ignore[reportCallIssue]

                return handler(**data)  # pyright: ignore[reportCallIssue]

            except SocketIOConnectionRefusedError:
                raise  # let this error bubble up to python-socketio
            except Exception as e:
                err_more = "".join(traceback.format_exception(e))  # noqa: F841
                err = "".join(traceback.format_exception_only(e))
                app.logger.exception(err)
                return err

    def _set_server(self, socketio: SocketIO) -> None:
        """Attach a Socket.IO server to this namespace.

        Args:
            socketio (SocketIO): SocketIO extension or async server.
        """
        from . import SocketIO

        if not self.socketio:
            self.socketio = socketio

        if isinstance(socketio, SocketIO):
            self.server = socketio.server

        elif isinstance(socketio, AsyncServer):
            self.server = socketio

    def set_socketio(self, socketio: SocketIO) -> None:
        """Attach the extension and middleware to this namespace.

        Args:
            socketio (SocketIO): SocketIO extension instance.
        """

        self._set_server(socketio)
        self.sockio_mw = socketio.sockio_mw

    def _set_socketio(self, socketio: SocketIO) -> None:
        """Attach the extension server to this namespace.

        Args:
            socketio (SocketIO): SocketIO extension instance.
        """

        self._set_server(socketio)

    async def emit(
        self,
        event: str,
        data: dict | None = None,
        room: str | None = None,
        *,
        include_self: bool = True,
        namespace: str | None = None,
        callback: Function | None = None,
    ) -> None:
        """Emit a custom event to one or more connected clients."""
        return await self.socketio.emit(
            event=event,
            data=data,
            room=room,
            include_self=include_self,
            namespace=namespace or self.namespace,
            callback=callback,
        )

    async def send(
        self,
        data: dict,
        room: str | None = None,
        *,
        include_self: bool = True,
        namespace: str | None = None,
        callback: Function | None = None,
    ) -> None:
        """Send a message to one or more connected clients."""
        return await self.socketio.send(
            data=data,
            room=room,
            include_self=include_self,
            namespace=namespace or self.namespace,
            callback=callback,
        )

    async def close_room(
        self,
        room: str,
        namespace: str | None = None,
    ) -> None:
        """Close a room."""
        return await self.socketio.close_room(
            room=room,
            namespace=namespace or self.namespace,
        )

    async def save_session(self, sid: str, session: SessionMixin) -> None:
        """Save a Socket.IO session in the current namespace.

        Args:
            sid (str): Socket.IO session ID.
            session (SessionMixin): Session data to save.
        """
        return await self.server.save_session(
            sid=sid,
            session=session,
            namespace=self.namespace,
        )

    def get_handler(self, event: str) -> Callable[..., Any] | None:
        """Return the handler method for an event name.

        Args:
            event (str): Socket.IO event name.

        Returns:
            Callable[..., Any] | None: Handler method when found.
        """
        return cast(
            "Callable[..., Any] | None",
            getattr(self, "on_" + (event or ""), None),
        )
