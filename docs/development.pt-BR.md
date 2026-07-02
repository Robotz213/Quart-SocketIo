# Desenvolvimento

## Qualidade

Comandos recomendados:

```bash
uv run ruff format .
uv run ruff check .
uv run pyright
uv run pytest
```

## Documentação

A documentação usa MkDocs com Material, i18n estático e mkdocstrings.

Para servir localmente:

```bash
uv run mkdocs serve
```

Para gerar o site estático:

```bash
uv run mkdocs build --strict
```

O resultado fica em `site/`.

## Estrutura relevante

```text
pulseio/
  __init__.py          # exports públicos
  main.py              # SocketIO e decorators de eventos
  core.py              # Controller, init_app, run, contexto Quart
  config.py            # defaults de configuração
  namespace.py         # Namespace baseado em socketio.AsyncNamespace
  middleware.py        # middleware ASGI e headers de proxy
  middleare.py         # shim de compatibilidade
  _utils.py            # helpers globais de contexto
  _uvicorn.py          # wrapper de runner Uvicorn
  common/exceptions.py # exceções customizadas
  _types/              # tipos internos
```

## Testes existentes

Os testes atuais cobrem:

- isolamento de defaults mutáveis de `Config`;
- isolamento de `SocketIO.environments`;
- exceções customizadas e helpers de raise;
- shim `pulseio.middleare`;
- seleção de headers confiáveis por hop;
- registro, despacho, namespaces e delegação de `SocketIO`.

## Checklist antes de publicar

```bash
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv run mkdocs build --strict
uv run python -m build
```
