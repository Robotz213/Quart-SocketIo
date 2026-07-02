from __future__ import annotations

from quart.sessions import SessionMixin


class _ManagedSession(dict, SessionMixin):
    """Manage user sessions for Quart-SocketIO.

    User sessions are stored as a simple dict, expanded with the Quart session
    attributes.
    """


__all__ = ["_ManagedSession"]
