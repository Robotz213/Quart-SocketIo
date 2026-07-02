# Roadmap de correcoes e melhorias

Este roadmap foi criado em 2026-07-02 a partir da leitura do projeto
`pulseio` e das regras declaradas em `pyproject.toml`.

Regras que guiam este plano:

- Python suportado: `>=3.13`.
- Ruff: `select = ["ALL"]`, `preview = true`, linha maxima de 79 caracteres,
  indentacao de 4 espacos e aspas duplas.
- Ruff format: `quote-style = "double"`, `indent-style = "space"` e formatacao
  de exemplos em docstrings.
- Pyright: `typeCheckingMode = "basic"` com `reportArgumentType = "none"`.
- O projeto usa `uv.lock`; o CI atual ainda usa `tox`.

## Estado atual

`pulseio` e uma biblioteca de integracao assincrona entre Quart e
python-socketio. O codigo ainda carrega partes herdadas de Quart-SocketIO e
Flask-SocketIO, com nomes antigos em README, URLs, templates de issue,
docstrings e configuracoes internas.

Comandos executados:

```bash
uv run ruff check .
uv run pyright
uv run pytest
```

Resultados:

- `ruff check` falha com 12 erros, todos em
  `pulseio/common/exceptions.py`, por `noqa` sem efeito.
- `pyright` falha com 54 erros e 3 avisos.
- `pytest` executa, mas coleta 0 testes.
- O workflow `.github/workflows/tests.yml` usa Python 3.8 a 3.12 e PyPy,
  embora o pacote declare `requires-python = ">=3.13"`.
- O CI chama `tox -eflake8`, `tox -edocs` e `tox`, mas nao ha `tox.ini` no
  checkout atual.
- `tests/` existe apenas com `__pycache__`.
- Ha um arquivo com typo publico: `pulseio/middleare.py`.
- Ha um atributo publico com typo: `SocketIO.enviroments`.

## Fase 1 - Restaurar base de qualidade

Prioridade: critica.

Objetivo: fazer as ferramentas oficiais do projeto medirem o estado real sem
depender de configuracao ausente.

- Adicionar dependencias de desenvolvimento no `pyproject.toml`, por exemplo
  `ruff`, `pyright`, `pytest`, `pytest-asyncio`, `pytest-cov` e `build`.
- Definir comandos oficiais para manutencao:
  - `uv run ruff format .`
  - `uv run ruff check .`
  - `uv run pyright`
  - `uv run pytest`
  - `uv run python -m build`
- Atualizar `.github/workflows/tests.yml` para instalar com `uv` e rodar os
  mesmos comandos locais.
- Trocar a matriz antiga de Python 3.8-3.12 por Python 3.13 e 3.14.
- Remover `tox` do CI ou adicionar um `tox.ini` real, se o projeto quiser
  manter tox como camada de orquestracao.
- Decidir se `.python-version` deve ficar em 3.14 ou se o ambiente local
  principal deve usar 3.13 para validar a versao minima.

Criterios de aceite:

- `uv sync --dev` prepara um ambiente completo.
- CI e ambiente local executam os mesmos comandos.
- O CI nao tenta testar versoes incompativeis com `requires-python`.

## Fase 2 - Corrigir excecoes publicas

Prioridade: critica.

Problemas observados:

- `QuartTypeError`, `QuartValueError`, `QuartRuntimeError` e
  `QuartSocketioError` recebem mensagem ou exception, mas chamam
  `super().__init__(*args)` e descartam o valor principal.
- `raise_runtime_error` levanta `QuartTypeError`, nao `QuartRuntimeError`.
- `raise_value_error` levanta `QuartTypeError`, nao `QuartValueError`.
- `type Any = any` usa o builtin `any`, que o Pyright interpreta como funcao,
  gerando erro.
- Os `noqa` em `exceptions.py` ignoram regras desativadas globalmente e por
  isso quebram Ruff.

Acoes:

- Substituir `type Any = any` por `from typing import Any`.
- Fazer as classes preservarem a mensagem recebida.
- Fazer `QuartSocketioError` preservar a exception original.
- Corrigir `raise_runtime_error`, `raise_value_error` e `raise_type_error`.
- Remover os `noqa` desnecessarios.
- Adicionar testes unitarios para mensagens e tipos levantados.

Criterios de aceite:

- `uv run ruff check .` passa.
- `raise_runtime_error("x")` levanta `QuartRuntimeError("x")`.
- `raise_value_error("x")` levanta `QuartValueError("x")`.
- Excecoes customizadas exibem mensagens uteis em tracebacks.

## Fase 3 - Isolar estado mutavel

Prioridade: alta.

Problemas observados:

- `Config.__init__` usa `super().__init__(DEFAULTS)`, compartilhando listas e
  dicts mutaveis de `DEFAULTS`.
- Defaults mutaveis incluem `handlers`, `extra_files`, `reloader_options`,
  `server_options`, `namespace_handlers`, `exception_handlers` e
  `transports`.
- `Controller` define `server`, `shutdown_event`, `config` e `sockio_mw` como
  atributos de classe.
- `SocketIO.enviroments` e `ClassVar`, entao ambientes por `sid` podem vazar
  entre instancias.

Acoes:

- Criar uma factory de defaults ou usar `copy.deepcopy(DEFAULTS)` em
  `Config.__init__`.
- Mover estado de runtime para atributos de instancia em `Controller`.
- Renomear `enviroments` para `environments`, mantendo alias temporario se a
  API publica ja tiver consumidores.
- Adicionar testes provando que duas instancias de `SocketIO` nao compartilham
  handlers, namespaces, sessoes, rooms ou environments.

Criterios de aceite:

- Alterar `Config()["handlers"]` nao altera outra instancia de `Config`.
- Duas instancias de `SocketIO` nao compartilham estado de conexao.

## Fase 4 - Corrigir fluxo de eventos

Prioridade: alta.

Problemas observados:

- `_trigger_event` monta `sid`, `event`, `namespace` e `environ` por indices
  de `args`; isso e fragil contra a assinatura real de python-socketio.
- `_handle_event` exige `event`, `namespace`, `sid`, `data` e `handler`, mas
  alguns chamadores repassam `kwargs` incompletos.
- Em `SocketIO.emit`, o wrapper de callback chama `_handle_event` por posicao
  incompativel com a assinatura atual.
- `send` chama `emit` de forma posicional, mas `SocketIO.emit` declara `event`
  como keyword-only.
- `handle_session` espera `environ`, mas recebe `request.namespace` ou uma
  string em alguns fluxos.
- `self.config["app"].error(err)` chama um metodo que Quart nao possui.
- `on_error` grava handlers em `self.config["debug"][namespace]`, embora
  `debug` seja booleano; deveria usar `exception_handlers`.

Acoes:

- Conferir a assinatura esperada de `AsyncServer._trigger_event` para a versao
  de `python-socketio` travada no lock.
- Normalizar um payload interno com campos explicitos: `event`, `namespace`,
  `sid`, `environ`, `data`, `handler`.
- Corrigir chamadas de `emit`, `send`, callbacks e `on_event` para usarem a
  mesma convencao de argumentos.
- Trocar `app.error` por `app.logger.exception` ou pelo fluxo configurado em
  `on_error` e `on_error_default`.
- Fazer `on_error` usar `exception_handlers`.
- Definir comportamento documentado para retorno de excecoes em handlers.

Criterios de aceite:

- Eventos `connect`, `disconnect`, `message`, `json` e eventos customizados
  funcionam com handlers async.
- Callbacks de `emit` executam com contexto correto.
- Handlers de erro por namespace e handler default sao chamados.

## Fase 5 - Tipagem e contrato publico

Prioridade: alta.

Problemas observados pelo Pyright:

- Atributos dinamicos `request.sid` e `request.namespace` nao existem nos tipos
  de Quart.
- `type Any = any` aparece em mais de um arquivo e quebra analise.
- `Function = Callable[P, T]` usa `ParamSpec` e `TypeVar` fora da lista de
  parametros do alias.
- Protocolos em `typing/_quart.py` declaram retorno, mas nao retornam valor.
- `get_namespace_handler` pode retornar `None`, mas anota `Namespace`.
- `get_environ` pode retornar `None`, mas anota `dict[str, Any]`.
- Tipos de `emit`, `send`, `on`, `event` e `_handle_event` nao refletem as
  chamadas reais.

Acoes:

- Substituir aliases caseiros de `Any` por `typing.Any`.
- Criar um tipo interno para request/websocket com `sid` e `namespace`, ou
  encapsular acesso dinamico via helpers tipados.
- Ajustar `Function`, `TExceptionHandler` e generics para Python 3.13+.
- Em `Protocol`, usar `...` nos corpos dos metodos.
- Anotar retornos opcionais como `Namespace | None` e
  `dict[str, Any] | None`, tratando os casos no chamador.
- Reduzir `pyright: ignore` aos casos inevitaveis, com comentario curto.

Criterios de aceite:

- `uv run pyright` passa sem erros.
- Ignorados restantes sao pontuais e explicados.

## Fase 6 - Compatibilidade e nomes

Prioridade: media-alta.

Acoes:

- Renomear `pulseio/middleare.py` para `pulseio/middleware.py`.
- Manter `middleare.py` como shim temporario importando de `middleware.py`.
- Renomear `enviroments` para `environments` com alias depreciado.
- Atualizar imports internos para o nome correto.
- Importar `SocketIOConnectionRefusedError` diretamente de
  `socketio.exceptions` em vez de depender de `pulseio.main`.
- Revisar `__all__` para exportar somente API publica intencional.

Criterios de aceite:

- Imports antigos continuam funcionando por uma versao menor.
- Novos nomes corretos aparecem em docs e exemplos.

## Fase 7 - Testes de regressao e integracao

Prioridade: media-alta.

Acoes:

- Criar testes com `pytest` e `pytest-asyncio`.
- Cobrir `Config` e defaults mutaveis.
- Cobrir excecoes customizadas.
- Cobrir helpers de contexto: `emit`, `send`, `call`, `join_room`,
  `leave_room`, `rooms`, `close_room` e `disconnect`.
- Cobrir middleware de proxy para:
  - `Forwarded`
  - `X-Forwarded-For`
  - `X-Forwarded-Proto`
  - `X-Forwarded-Host`
  - `SOCKETIO_TRUSTED_HOPS`
- Criar smoke test Quart + Socket.IO com cliente assincrono.
- Testar namespace baseado em classe.
- Testar o comportamento de `manage_session=True` e `manage_session=False`.

Criterios de aceite:

- `uv run pytest` coleta e executa testes reais.
- Fluxos publicos principais tem regressao automatizada.

## Fase 8 - Dependencias e empacotamento

Prioridade: media.

Acoes:

- Avaliar se `clear` deve ser dependencia runtime. Limpar terminal no shutdown
  nao parece essencial para uma biblioteca.
- Avaliar se `hypercorn` deve ser dependencia obrigatoria, extra opcional ou
  removida enquanto o runner implementado usa Uvicorn.
- Criar extras opcionais para filas, se aplicavel:
  - Redis
  - Kafka
  - ZeroMQ
  - Kombu
- Atualizar `project.urls` para o repositorio definitivo de `Quart-SocketIo`.
- Verificar `MANIFEST.in` para incluir apenas arquivos necessarios.
- Validar wheel e sdist em ambiente limpo.

Criterios de aceite:

- `uv run python -m build` gera artefatos instalaveis.
- Instalar a wheel em ambiente limpo permite `import pulseio`.
- Dependencias runtime sao apenas as necessarias para uso basico.

## Fase 9 - Documentacao e identidade

Prioridade: media.

Acoes:

- Atualizar README para `pulseio` como nome principal.
- Corrigir links de `Quart-SocketIO`, Flask-SocketIO e repositorios antigos.
- Corrigir templates em `.github/ISSUE_TEMPLATE`, incluindo `SockertIO`.
- Remover ou consertar textos com mojibake, como palavras acentuadas
  quebradas.
- Documentar suporte real a Python 3.13 e 3.14.
- Documentar comandos de desenvolvimento com `uv`.
- Documentar exemplos para:
  - app minimo Quart
  - namespaces
  - rooms
  - callbacks
  - deploy com Uvicorn
  - uso atras de proxy

Criterios de aceite:

- Exemplo do README roda em app minimo.
- Links apontam para o projeto atual.
- Documentacao nao referencia ferramentas ausentes.

## Fase 10 - Release

Prioridade: baixa-media.

Acoes:

- Definir versionamento semantico.
- Criar changelog.
- Criar checklist de release:
  - `uv run ruff format --check .`
  - `uv run ruff check .`
  - `uv run pyright`
  - `uv run pytest`
  - `uv run python -m build`
  - smoke test de instalacao da wheel
- Marcar aliases depreciados para remocao futura.
- Publicar notas separando correcoes de bug, mudancas de API e melhorias de
  documentacao.

Criterios de aceite:

- Release pode ser reproduzida por comandos documentados.
- Mudancas incompativeis sao explicitamente comunicadas.

## Ordem sugerida

1. Corrigir tooling e CI.
2. Corrigir excecoes e Ruff.
3. Isolar estado mutavel.
4. Adicionar testes de regressao para os bugs corrigidos.
5. Corrigir fluxo de eventos, sessoes e callbacks.
6. Resolver Pyright.
7. Renomear typos com compatibilidade.
8. Limpar dependencias, empacotamento e documentacao.
9. Preparar release.

## Checklist rapido

- [ ] Ambiente dev declarado em `pyproject.toml`.
- [ ] CI alinhado a Python `>=3.13`.
- [ ] `uv run ruff check .` passando.
- [ ] `uv run ruff format --check .` passando.
- [ ] `uv run pyright` passando.
- [ ] `uv run pytest` coletando e passando testes.
- [ ] Excecoes customizadas corrigidas.
- [ ] Defaults mutaveis isolados por instancia.
- [ ] Fluxo de eventos e callbacks validado.
- [ ] Sessoes validadas com `manage_session=True` e `False`.
- [ ] `middleare` e `enviroments` tratados com compatibilidade.
- [ ] README, issue templates e URLs atualizados.
- [ ] Build de wheel/sdist validado em ambiente limpo.
