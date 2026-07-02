# Desenvolvimento

## Qualidade

Comandos recomendados:

```bash
uv run ruff format .
uv run ruff check .
uv run pyright
uv run pytest
```

## Documentacao

A documentacao usa MkDocs com Material e mkdocstrings.

Para servir localmente:

```bash
uv run mkdocs serve
```

Para gerar o site estatico:

```bash
uv run mkdocs build --strict
```

O resultado fica em `site/`.

## Estrutura relevante

```text
pulseio/
  __init__.py          # exports publicos
  main.py              # SocketIO e decorators de eventos
  core.py              # Controller, init_app, run, contexto Quart
  config.py            # defaults de configuracao
  namespace.py         # Namespace baseado em socketio.AsyncNamespace
  middleware.py        # middleware ASGI e headers de proxy
  middleare.py         # shim de compatibilidade
  _utils.py            # helpers globais de contexto
  _uvicorn.py          # wrapper de runner Uvicorn
  common/exceptions.py # excecoes customizadas
  _types/              # tipos internos
```

## Testes existentes

Os testes atuais cobrem:

- isolamento de defaults mutaveis de `Config`;
- isolamento de `SocketIO.environments`;
- excecoes customizadas e helpers de raise;
- shim `pulseio.middleare`;
- selecao de headers confiaveis por hop.

## Checklist antes de publicar

```bash
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv run mkdocs build --strict
uv run python -m build
```
