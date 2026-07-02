## [GH-3] refact - Reestrutura SocketIO e documentação

---

## 📖 Descrição

Este Pull Request reorganiza a biblioteca para consolidar a integração
assíncrona entre Quart e Socket.IO sob o pacote `quart_socketio`, moderniza a
documentação e reforça a base de qualidade do projeto.

O objetivo principal é alinhar nome, estrutura, documentação, testes e tooling
ao estado atual da biblioteca. A mudança foi motivada pela necessidade de
padronizar a identidade do pacote, substituir a documentação Sphinx por MkDocs
bilíngue e aumentar a cobertura dos contratos públicos do SocketIO.

O impacto esperado é um projeto mais consistente para manutenção, com
documentação em inglês por padrão, opção em português brasileiro, CI mais
alinhado ao ambiente atual e testes automatizados cobrindo comportamentos
centrais.

## ✨ Tipo de Mudança

- [ ] Nova funcionalidade
- [ ] Correção de bug
- [x] Refatoração
- [ ] Melhoria de performance
- [x] Ajustes estruturais / organização de código
- [x] Infraestrutura / configuração
- [x] Documentação
- [ ] Outro (descrever abaixo)

## 🧩 O que foi alterado

- Renomeia e reorganiza o pacote principal de `pulseio` para
  `quart_socketio`, incluindo módulos internos, tipos auxiliares, exceções,
  middleware e exports públicos.
- Substitui a documentação Sphinx por MkDocs com Material, `mkdocstrings` e
  suporte a i18n estático.
- Define inglês como idioma padrão da documentação e adiciona versões em
  português brasileiro com ortografia revisada.
- Adiciona documentação de instalação, primeiro app, eventos, namespaces,
  rooms, configuração, deploy, arquitetura interna, desenvolvimento e API.
- Atualiza CI, dependências de desenvolvimento, manifesto, README e arquivos de
  configuração relacionados à qualidade do projeto.
- Adiciona testes unitários para `SocketIO`, middleware, exceções e
  configuração.
- Ajusta a versão do projeto para `0.0.1`.

## 🏗️ Impacto Técnico

- A estrutura do pacote muda para `quart_socketio`, com atualização dos imports
  internos e organização dos tipos em `_types`.
- A documentação passa a ser gerada por MkDocs e não mais por Sphinx.
- O build do pacote passa a restringir a descoberta de pacotes a
  `quart_socketio*`, evitando inclusão acidental de diretórios como `site/`.
- A suíte de testes passa a validar o registro e despacho de eventos,
  namespaces, delegação de métodos do SocketIO, isolamento de configuração,
  exceções customizadas e middleware.
- O CI e o ambiente de desenvolvimento ficam mais próximos dos comandos locais
  baseados em `uv`, `ruff`, `pyright`, `pytest` e `mkdocs`.

## ⚠️ Breaking Changes

- [ ] Não
- [x] Sim (descrever abaixo)

O pacote principal foi renomeado de `pulseio` para `quart_socketio`.
Consumidores que importam `pulseio` precisarão ajustar imports para o novo
nome do pacote.

## 🧪 Testes e Validação

As mudanças foram validadas com:

- `uv run pytest`
- `uv run ruff check .`
- `uv run pyright`
- `uv run ruff format --check .`
- `uv run mkdocs build --strict`

Cenários cobertos pelos testes:

- configuração e isolamento de defaults mutáveis;
- exceções customizadas;
- middleware e compatibilidade de import;
- registro, despacho, namespaces e delegações de `SocketIO`.

## 🧹 Manutenção e Qualidade

- [x] Código morto removido
- [x] Imports/arquivos desnecessários removidos
- [x] Melhorias de legibilidade
- [x] Tipagem ou validações aprimoradas
- [x] Comentários ou documentação adicionados

## 📚 Observações para Revisão

- A PR é ampla porque combina renomeação estrutural, documentação, testes e
  ajustes de qualidade.
- O ponto principal de atenção é a mudança de import público para
  `quart_socketio`.
- A documentação nova mantém a menção de inspiração no Flask-SocketIO, projeto
  de Miguel Grinberg.
- O arquivo `middleare.py` permanece como shim de compatibilidade para o typo
  histórico.

## 🚀 Próximos Passos (Opcional)

- Avaliar se será necessário manter um pacote shim `pulseio` em uma próxima
  versão para facilitar migração de usuários existentes.
- Preparar changelog e checklist de release para publicação.
