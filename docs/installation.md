# Instalacao

## Como dependencia

Enquanto o pacote nao estiver publicado no PyPI, instale direto do repositorio:

```bash
pip install git+https://github.com/Robotz213/PulseIo.git
```

O projeto declara suporte a Python `>=3.13`.

## Ambiente de desenvolvimento

O repositorio usa `uv` para resolver dependencias:

```bash
uv sync --all-extras --dev
```

Depois disso, os comandos de manutencao ficam disponiveis:

```bash
uv run ruff format .
uv run ruff check .
uv run pyright
uv run pytest
uv run mkdocs build --strict
```

## Dependencias de runtime

PulseIo depende de:

- `quart`
- `python-socketio`
- `uvicorn`
- `hypercorn`
- `websockets`
- `clear`

O runner implementado no codigo usa Uvicorn por padrao.
