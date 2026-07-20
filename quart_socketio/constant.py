from logging.config import dictConfig

ACCESS_FMT = (
    '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
)


def load_log_config(**kwargs: str) -> dict[str, str]:

    log_level = kwargs.get("log_level", "info")
    cfg_ = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": "%(levelprefix)s %(asctime)s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "access": {
                "()": "uvicorn.logging.AccessFormatter",
                "fmt": ACCESS_FMT,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
            "access": {
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "uvicorn": {"handlers": ["default"], "level": log_level},
            "uvicorn.error": {
                "handlers": ["default"],
                "level": log_level,
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["access"],
                "level": log_level,
                "propagate": False,
            },
            "uvicorn.asgi": {
                "handlers": ["default"],
                "level": log_level,
                "propagate": False,
            },
            "uvicorn.lifespan": {
                "handlers": ["default"],
                "level": log_level,
                "propagate": False,
            },
        },
    }
    dictConfig(cfg_)

    return cfg_
