# Contribuindo

O Quart-SocketIo aceita contribuicoes em codigo, testes, documentacao,
exemplos e manutencao do projeto.

Antes de iniciar qualquer contribuicao, leia o guia de contribuicao do projeto:

- [CONTRIBUTING.md](https://github.com/Robotz213/Quart-SocketIo/blob/dev/contributing.md)

As regras mais importantes do fluxo sao:

- Toda contribuicao precisa estar vinculada a uma issue existente antes da
  criacao da branch.
- Todas as branches de contribuicao precisam ser criadas a partir de `dev`.
- Pull requests devem apontar para `dev`.
- Mudancas na documentacao devem manter as paginas em ingles e portugues do
  Brasil alinhadas quando ambas existirem.

Para trabalhar localmente na documentacao, instale as dependencias de
desenvolvimento e execute:

```bash
uv sync --all-extras --dev
uv run mkdocs serve
uv run mkdocs build --strict
```

Ao alterar comportamento publico, atualize a pagina de documentacao relevante e
rode o build da documentacao antes de abrir um pull request.
