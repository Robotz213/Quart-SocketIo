# Changelog

Todas as mudancas relevantes deste projeto serao documentadas neste arquivo.

## [0.0.1] - 2026-07-02

### Adicionado

- Primeira versao publica do pacote `quart_socketio`.
- Integracao assincrona de Socket.IO para aplicacoes Quart.
- Classe `SocketIO` para inicializacao direta ou tardia com uma aplicacao Quart.
- Decoradores e registro de eventos Socket.IO.
- Suporte a namespaces, salas e gerenciamento de conexoes.
- Helpers de contexto para handlers, incluindo `emit`, `send`, `call`,
  `join_room`, `leave_room`, `close_room`, `rooms` e `disconnect`.
- Middleware ASGI para integrar Quart e o servidor Socket.IO.
- Configuracao centralizada por meio da classe `Config`.
- Excecoes publicas e tipos auxiliares para a API interna.

### Documentacao

- Documentacao com MkDocs e Material for MkDocs.
- Conteudo em ingles e portugues do Brasil.
- Guias de instalacao, quickstart, configuracao, eventos, namespaces, salas,
  deployment, desenvolvimento, internos e API publica.
- Configuracao do Read the Docs para publicacao da documentacao.

### Qualidade e Manutencao

- Configuracao de lint e formatacao com Ruff.
- Configuracao de checagem de tipos com Pyright.
- Testes automatizados com Pytest e cobertura de testes.
- Workflows de CI para qualidade, testes em multiplos sistemas operacionais e
  envio de cobertura.
- Workflow de publicacao de pacote Python via GitHub Actions.

### Alterado

- Projeto renomeado de `pulseio` para `quart_socketio`.
- Repositorio e links de documentacao atualizados para `Quart-SocketIo`.
- Versao do pacote ajustada para `0.0.1`.
