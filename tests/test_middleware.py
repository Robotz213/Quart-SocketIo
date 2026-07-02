from pulseio.middleare import QuartSocketIOMiddleware as CompatMiddleware
from pulseio.middleware import QuartSocketIOMiddleware, _get_trusted_value


def test_middleare_compatibility_shim_exports_middleware() -> None:
    assert CompatMiddleware is QuartSocketIOMiddleware


def test_get_trusted_value_uses_configured_hop_from_right() -> None:
    headers = [(b"x-forwarded-for", b"198.51.100.1, 203.0.113.10")]

    assert _get_trusted_value(b"x-forwarded-for", headers, 1) == (
        "203.0.113.10"
    )
    assert _get_trusted_value(b"x-forwarded-for", headers, 2) == (
        "198.51.100.1"
    )


def test_get_trusted_value_ignores_untrusted_headers() -> None:
    headers = [(b"x-forwarded-proto", b"https")]

    assert _get_trusted_value(b"x-forwarded-proto", headers, 0) is None
    assert _get_trusted_value(b"x-forwarded-host", headers, 1) is None
