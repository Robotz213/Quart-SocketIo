import pytest
from quart_socketio.common.exceptions import (
    QuartRuntimeError,
    QuartSocketioError,
    QuartTypeError,
    QuartValueError,
    raise_runtime_error,
    raise_type_error,
    raise_value_error,
)


def test_custom_exceptions_preserve_message() -> None:
    assert str(QuartTypeError("bad type")) == "bad type"
    assert str(QuartValueError("bad value")) == "bad value"
    assert str(QuartRuntimeError("bad runtime")) == "bad runtime"
    assert str(QuartSocketioError(RuntimeError("socket failed"))) == (
        "socket failed"
    )


def test_raise_helpers_raise_specific_exception_types() -> None:
    with pytest.raises(QuartTypeError, match="type"):
        raise_type_error("type")

    with pytest.raises(QuartValueError, match="value"):
        raise_value_error("value")

    with pytest.raises(QuartRuntimeError, match="runtime"):
        raise_runtime_error("runtime")
