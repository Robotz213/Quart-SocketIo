from __future__ import annotations

from typing import Any, NoReturn


class QuartTypeError(TypeError):
    """Represent an invalid Quart-SocketIO type usage."""

    def __init__(self, message: str, *args: Any) -> None:
        """Create a type error with the provided message.

        Args:
            message (str): Error message to display.
            *args (Any): Additional exception arguments.
        """
        super().__init__(message, *args)


class QuartValueError(ValueError):
    """Represent an invalid Quart-SocketIO value."""

    def __init__(self, message: str, *args: Any) -> None:
        """Create a value error with the provided message.

        Args:
            message (str): Error message to display.
            *args (Any): Additional exception arguments.
        """
        super().__init__(message, *args)


class QuartRuntimeError(RuntimeError):
    """Represent a Quart-SocketIO runtime failure."""

    def __init__(self, message: str, *args: Any) -> None:
        """Create a runtime error with the provided message.

        Args:
            message (str): Error message to display.
            *args (Any): Additional exception arguments.
        """
        super().__init__(message, *args)


class QuartSocketioError(Exception):
    """Represent a generic Quart-SocketIO exception."""

    def __init__(self, exc: Exception | str, *args: Any) -> None:
        """Create a SocketIO error from a message or exception.

        Args:
            exc (Exception | str): Original exception or message.
            *args (Any): Additional exception arguments.
        """
        super().__init__(exc, *args)


def raise_runtime_error(message: str) -> NoReturn:
    """Raise a Quart-SocketIO runtime error.

    Args:
        message (str): Error message to display.

    Raises:
        QuartRuntimeError: Always raised with the provided message.
    """
    raise QuartRuntimeError(message=message)


def raise_value_error(message: str) -> NoReturn:
    """Raise a Quart-SocketIO value error.

    Args:
        message (str): Error message to display.

    Raises:
        QuartValueError: Always raised with the provided message.
    """
    raise QuartValueError(message=message)


def raise_type_error(message: str) -> NoReturn:
    """Raise a Quart-SocketIO type error.

    Args:
        message (str): Error message to display.

    Raises:
        QuartTypeError: Always raised with the provided message.
    """
    raise QuartTypeError(message=message)
