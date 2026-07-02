# Instalação

## Como dependência

Enquanto o pacote não estiver publicado no PyPI, instale-o diretamente do
repositório:

```bash
pip install git+https://github.com/Robotz213/PulseIo.git
```

O projeto declara suporte a Python `>=3.13`.

## Ambiente de desenvolvimento

O repositório usa `uv` para resolver dependências:

```bash
uv sync --all-extras --dev
```

Depois disso, os comandos de manutenção ficam disponíveis:

```bash
uv run ruff format .
uv run ruff check .
uv run pyright
uv run pytest
uv run mkdocs build --strict
```

## Dependências de runtime

PulseIo depende de:

- `quart`
- `python-socketio`
- `uvicorn`
- `hypercorn`
- `websockets`
- `clear`

O runner implementado no código usa Uvicorn por padrão.
