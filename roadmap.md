# Roadmap de correcoes e melhorias

Este roadmap foi criado a partir da leitura do projeto `pulseio` e das regras
definidas em `pyproject.toml`: Python `>=3.13`, Ruff com `select = ["ALL"]`,
linha maxima de 79 caracteres, formatacao com aspas duplas e Pyright em modo
`basic`.

## Estado atual observado

- O pacote implementa uma integracao assincrona entre Quart e Socket.IO, mas
  ainda carrega nomes, docs e CI herdados de `Quart-SocketIO`/Flask-SocketIO.
- O projeto nao possui suite de testes no checkout atual.
- `ruff` e `pyright` estao configurados, mas nao aparecem como dependencias de
  desenvolvimento no `pyproject.toml`.
- O CI em `.github/workflows/tests.yml` usa `tox -eflake8`, mas nao ha
  `tox.ini`, `.flake8` ou `setup.cfg` no repositorio.
- O CI testa Python 3.8-3.12 e PyPy, enquanto `pyproject.toml` exige Python
  `>=3.13`.
- `.python-version` aponta para `3.14`, compativel com `>=3.13`, mas diferente
  da maior parte do lock e do CI esperado.
- Os arquivos `poetry.toml` e `poetry.lock` citados no IDE nao existem neste
  checkout; o projeto parece estar usando `uv.lock`.

## Resultado das ferramentas

Comandos executados:

```bash
uvx ruff check .
uvx pyright
```

Resultado resumido:

- Ruff encontrou 29 erros. Os principais estao em `docs/conf.py` e
  `pulseio/common/exceptions.py`, incluindo linhas longas, codigo comentado,
  `noqa` sem efeito e declaracao de encoding desnecessaria.
- Pyright reportou 62 erros e 3 avisos. Parte dos erros veio do ambiente do
  `uvx` nao resolver dependencias instaladas do projeto, mas ha problemas reais
  de tipagem, assinatura, retorno e imports.

## Fase 1 - Alinhar tooling e CI

Prioridade: alta.

- Adicionar grupos de dependencias de desenvolvimento no `pyproject.toml`, por
  exemplo `ruff`, `pyright`, `pytest`, `pytest-asyncio`, `sphinx` e ferramentas
  de cobertura.
- Definir comandos oficiais no README ou em um task runner simples:
  `uv run ruff format .`, `uv run ruff check .`, `uv run pyright` e
  `uv run pytest`.
- Atualizar o workflow GitHub Actions para Python 3.13 e 3.14, removendo a
  matriz antiga de 3.8-3.12 se o pacote realmente requer `>=3.13`.
- Substituir `tox -eflake8` por Ruff/Pyright ou adicionar um `tox.ini` real se
  a manutencao com tox for desejada.
- Decidir uma unica ferramenta de lock/ambiente: `uv` ou Poetry. Se for `uv`,
  remover referencias operacionais a Poetry; se for Poetry, restaurar
  `poetry.toml` e `poetry.lock`.

Criterio de aceite:

- `uv sync --all-extras --dev` prepara um ambiente completo.
- CI executa lint, type check, docs e testes usando a mesma versao minima de
  Python declarada no pacote.

## Fase 2 - Corrigir erros que quebram contrato publico

Prioridade: alta.

- Corrigir `pulseio/common/exceptions.py`:
  - `QuartTypeError`, `QuartValueError`, `QuartRuntimeError` e
    `QuartSocketioError` devem preservar a mensagem/exception recebida.
  - `raise_runtime_error` deve levantar `QuartRuntimeError`.
  - `raise_value_error` deve levantar `QuartValueError`.
  - `raise_type_error` deve continuar levantando `QuartTypeError`.
- Remover aliases invalidos ou perigosos como `type Any = any` e
  `type Any = object`; usar `typing.Any` onde o contrato exige valor dinamico.
- Corrigir `pulseio/namespace.py`, que importa
  `SocketIOConnectionRefusedError` de `pulseio.main`, mas esse simbolo nao e
  exportado por `main.py`. Preferir importar diretamente de
  `socketio.exceptions`, como ja ocorre em `pulseio/main.py`.
- Corrigir o typo `enviroments` para `environments`, mantendo compatibilidade
  temporaria se isso ja for usado externamente.
- Corrigir o typo do arquivo `pulseio/middleare.py` para
  `pulseio/middleware.py`, com shim de compatibilidade se necessario.

Criterio de aceite:

- Excecoes carregam mensagens corretas.
- Imports publicos funcionam sem depender de efeitos colaterais.
- Alteracoes incompativeis sao documentadas ou protegidas por aliases
  temporarios.

## Fase 3 - Eliminar estado compartilhado acidental

Prioridade: alta.

- Revisar `pulseio/config.py`: `DEFAULTS` usa listas e dicts mutaveis
  compartilhados, como `handlers`, `extra_files`, `reloader_options`,
  `server_options`, `namespace_handlers` e `exception_handlers`.
- Garantir que cada `Config()` receba copias novas dos defaults.
- Avaliar trocar `UserDict` por um modelo tipado mais explicito ou uma factory
  de defaults.
- Revisar atributos de classe em `Controller`, como `shutdown_event`, `server`,
  `config` e `sockio_mw`, para evitar compartilhamento entre instancias.
- Revisar `SocketIO.enviroments`, hoje `ClassVar`, porque ambientes por `sid`
  podem vazar entre instancias de `SocketIO`.

Criterio de aceite:

- Duas instancias independentes de `SocketIO` nao compartilham handlers,
  namespaces, excecoes, sessoes ou ambientes.

## Fase 4 - Corrigir fluxo de eventos e sessoes

Prioridade: alta.

- Revisar `_trigger_event`, `_handle_event` e `_update_kwargs` em
  `pulseio/main.py`; a montagem manual de `sid`, `event`, `namespace` e `data`
  por posicao em `args` e fragil.
- Corrigir chamadas suspeitas de `handle_session`: em alguns pontos o metodo
  espera `environ`, mas recebe `request.namespace` ou string similar.
- Corrigir `self.config["app"].error(err)`, pois `Quart` usa logger e handlers
  de erro, nao um metodo generico `.error`.
- Revisar callbacks em `emit`; a chamada para `_handle_event` parece usar ordem
  posicional incompativel com a assinatura atual.
- Decidir se exceptions em handlers devem ser retornadas como string ou
  repassadas para handlers configurados em `on_error`/`on_error_default`.
- Garantir que eventos `connect`, `disconnect`, eventos customizados e
  namespaces de classe tenham comportamento identico ao esperado em
  python-socketio.

Criterio de aceite:

- Testes cobrem `connect`, `disconnect`, `emit`, `send`, `call`, rooms,
  namespace default e namespace customizado.
- Erros de handlers acionam o mecanismo de erro documentado.

## Fase 5 - Tipagem e API publica

Prioridade: media-alta.

- Revisar `pulseio/typing/*`; ha `ParamSpec` e type aliases que o Pyright nao
  consegue validar.
- Ajustar o retorno de `get_namespace_handler`, que hoje pode retornar `None`
  apesar da anotacao indicar `Namespace`.
- Ajustar `CustomJsonClass` em `pulseio/typing/_quart.py`; metodos de
  `Protocol` com corpo apenas docstring devem usar `...` para satisfazer
  Pyright.
- Reduzir `pyright: ignore` e `noqa` aos casos realmente inevitaveis.
- Revisar assinaturas publicas de `SocketIO.on`, `SocketIO.event`,
  `SocketIO.emit`, `SocketIO.send`, `Namespace.emit` e helpers em `_utils.py`.

Criterio de aceite:

- `uv run pyright` passa sem erros.
- Os ignores restantes tem motivo claro e localizado.

## Fase 6 - Conformidade Ruff

Prioridade: media.

- Aplicar `ruff format` respeitando `line-length = 79` e aspas duplas.
- Corrigir `docs/conf.py` ou ajustar o ignore de docs se a intencao for manter
  um arquivo Sphinx gerado por template.
- Remover `noqa` sem efeito e comentarios de codigo morto.
- Reduzir `except Exception` amplo nos pontos em que o tipo esperado e
  conhecido.
- Substituir `print("Server stopped!")` em shutdown por logging.
- Avaliar se as regras globais ignoradas em `pyproject.toml` ainda fazem
  sentido: `D`, `SLF001`, `FIX`, `PYI021`, `PLC`, `PLR`, `ARG`, `PD`.

Criterio de aceite:

- `uv run ruff check .` e `uv run ruff format --check .` passam.

## Fase 7 - Testes

Prioridade: media-alta.

- Criar estrutura `tests/` com `pytest` e `pytest-asyncio`.
- Testar `Config` para garantir que defaults mutaveis nao sao compartilhados.
- Testar excecoes customizadas e helpers `raise_*`.
- Testar middleware de headers proxy:
  - `Forwarded`
  - `X-Forwarded-For`
  - `X-Forwarded-Proto`
  - `X-Forwarded-Host`
  - `SOCKETIO_TRUSTED_HOPS`
- Testar integracao minima Quart + Socket.IO com cliente assincrono.
- Adicionar testes de regressao para namespace baseado em classe.

Criterio de aceite:

- Suite roda localmente e no CI.
- Cobertura inclui os fluxos publicos mais usados por consumidores da
  biblioteca.

## Fase 8 - Documentacao e identidade do projeto

Prioridade: media.

- Atualizar README e docs para o nome `pulseio`, mantendo nota historica sobre
  a origem em Flask-SocketIO/Quart-SocketIO se desejado.
- Atualizar `docs/conf.py`: `project`, `author`, repo GitHub, titulos e nomes
  de artefatos.
- Revisar exemplos do README para refletir assinaturas reais.
- Corrigir textos com encoding quebrado, como contracoes e palavras acentuadas
  renderizadas com mojibake.
- Documentar suporte real a Python 3.13/3.14.
- Documentar modo de deploy com Uvicorn e Hypercorn, ou remover Hypercorn se
  nao houver suporte implementado.

Criterio de aceite:

- Docs constroem sem warnings relevantes.
- Exemplos copiados da documentacao executam em um app Quart minimo.

## Fase 9 - Dependencias e empacotamento

Prioridade: media.

- Revisar se `clear` precisa ser dependencia runtime; limpar terminal no
  shutdown nao parece essencial para uma biblioteca.
- Verificar se `hypercorn` deve ser dependencia obrigatoria, extra opcional ou
  removida enquanto o launch mode real usa Uvicorn.
- Definir extras opcionais para filas:
  - Redis
  - Kafka
  - ZeroMQ
  - Kombu
- Atualizar `project.urls` para o repositorio definitivo.
- Garantir que `MANIFEST.in` inclui docs e arquivos necessarios, mas nao
  artefatos locais.

Criterio de aceite:

- `python -m build` gera wheel/sdist instalaveis.
- Instalar o pacote em ambiente limpo permite importar `pulseio` e executar um
  app minimo.

## Fase 10 - Compatibilidade e release

Prioridade: baixa-media.

- Definir politica de versionamento semantico para correcoes que alteram API.
- Se renomear `middleare.py` e `enviroments`, manter aliases depreciados por
  uma versao menor antes de remover.
- Publicar changelog com:
  - correcoes de exceptions
  - correcoes de evento/sessao
  - mudancas de suporte a Python
  - mudancas de docs e empacotamento
- Criar checklist de release com lint, type check, testes, build e smoke test.

Criterio de aceite:

- Uma nova release pode ser reproduzida a partir de comandos documentados.

## Ordem sugerida de execucao

1. Corrigir tooling/CI para conseguir medir o progresso.
2. Corrigir excecoes, imports quebrados e estado compartilhado.
3. Adicionar testes de regressao para os bugs corrigidos.
4. Corrigir fluxo de eventos/sessoes com testes de integracao.
5. Limpar tipagem e Ruff ate `pyright` e `ruff` passarem.
6. Atualizar docs, README, empacotamento e release.

## Checklist rapido

- [ ] Ambiente dev declarado no `pyproject.toml`.
- [ ] CI alinhado a Python `>=3.13`.
- [ ] Ruff passando.
- [ ] Pyright passando.
- [ ] Tests criados e passando.
- [ ] Excecoes customizadas corrigidas.
- [ ] Defaults mutaveis isolados por instancia.
- [ ] Imports e nomes com typo tratados com compatibilidade.
- [ ] Fluxo Socket.IO validado por testes.
- [ ] README/docs atualizados para `pulseio`.
- [ ] Build wheel/sdist validado em ambiente limpo.
