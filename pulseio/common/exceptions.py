from __future__ import annotations

from typing import Any, NoReturn


class QuartTypeError(TypeError):
    def __init__(self, message: str, *args: Any) -> None:
        super().__init__(message, *args)


class QuartValueError(ValueError):
    def __init__(self, message: str, *args: Any) -> None:
        super().__init__(message, *args)


class QuartRuntimeError(RuntimeError):
    def __init__(self, message: str, *args: Any) -> None:
        super().__init__(message, *args)


class QuartSocketioError(Exception):
    def __init__(self, exc: Exception | str, *args: Any) -> None:
        super().__init__(exc, *args)


def raise_runtime_error(message: str) -> NoReturn:
    raise QuartRuntimeError(message=message)


def raise_value_error(message: str) -> NoReturn:
    raise QuartValueError(message=message)


def raise_type_error(message: str) -> NoReturn:
    raise QuartTypeError(message=message)
