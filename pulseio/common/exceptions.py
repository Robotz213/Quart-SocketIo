from __future__ import annotations

from typing import TYPE_CHECKING, NoReturn

if TYPE_CHECKING:
    from pulseio._types import Any


class QuartTypeError(TypeError):
    def __init__(self, message: str, *args: Any) -> None:
        super().__init__(*args)


class QuartValueError(ValueError):
    def __init__(self, message: str, *args: Any) -> None:
        super().__init__(*args)


class QuartRuntimeError(RuntimeError):
    def __init__(self, message: str, *args: Any) -> None:
        super().__init__(*args)


class QuartSocketioError(Exception):
    def __init__(self, exc: Exception, *args: Any) -> None:

        super().__init__(*args)


def raise_runtime_error(message: str) -> NoReturn:
    raise QuartTypeError(message=message)


def raise_value_error(message: str) -> NoReturn:
    raise QuartTypeError(message=message)


def raise_type_error(message: str) -> NoReturn:
    raise QuartTypeError(message=message)
