# Contributing

Quart-SocketIo welcomes contributions to code, tests, documentation, examples,
and project maintenance.

Before starting any contribution, read the project contribution guide:

- [CONTRIBUTING.md](https://github.com/Robotz213/Quart-SocketIo/blob/dev/contributing.md)

The most important workflow rules are:

- Every contribution must be linked to an existing issue before a branch is
  created.
- All contribution branches must be created from `dev`.
- Pull requests should target `dev`.
- Documentation changes should keep the English and Brazilian Portuguese pages
  aligned when both versions exist.

For local documentation work, install the development dependencies and run:

```bash
uv sync --all-extras --dev
uv run mkdocs serve
uv run mkdocs build --strict
```

When changing public behavior, update the relevant documentation page and run
the docs build before opening a pull request.
