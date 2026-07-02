# Contributing

Thank you for considering a contribution to Quart-SocketIo. This project
provides async Socket.IO integration for Quart applications, inspired by the
developer experience of Flask-SocketIO.

These guidelines help contributors and maintainers keep work clear, reviewable,
and easy to merge.

## Ways to Contribute

Helpful contributions include:

- Bug reports with clear reproduction steps.
- Fixes for confirmed issues.
- Documentation improvements and examples.
- Tests that cover existing or new behavior.
- Small maintenance improvements that keep the project healthy.
- Feature proposals that fit the goal of providing a clean Socket.IO extension
  for Quart.

Please do not use the issue tracker for private security reports. See
[Security](#security) instead.

## Ground Rules

- Be respectful and constructive in issues, reviews, and discussions.
- Keep changes focused. A pull request should solve one issue or one closely
  related set of changes.
- Do not start work without a linked issue.
- Do not create contribution branches from `main`.
- Add or update tests when behavior changes.
- Update documentation when public behavior, configuration, or usage changes.
- Keep the public API stable unless the linked issue explicitly discusses a
  breaking change.

## Before You Create a Branch

Every contribution branch must be linked to an existing issue.

Before creating a branch:

1. Search the issue tracker to see whether the work is already being discussed.
2. Create a new issue if one does not exist.
3. Wait for the issue to be accepted or clarified when the change is not
   obvious.
4. Create your branch from `dev`.

All contribution branches must start from `dev`. Branches created from `main`
may be asked to rebase or recreate the branch before review.

Example:

```bash
git checkout dev
git pull origin dev
git checkout -b issue-123-fix-socketio-handler
```

Use a branch name that references the issue, such as:

```text
issue-123-fix-socketio-handler
issue-124-docs-configuration
issue-125-add-namespace-test
```

## Development Setup

This project uses Python 3.13 or newer and `uv` for local development.

Install the development environment:

```bash
uv sync --all-extras --dev
```

Useful local commands:

```bash
uv run ruff format .
uv run ruff check .
uv run pyright
uv run pytest
uv run mkdocs serve
```

Build the documentation locally:

```bash
uv run mkdocs build --strict
```

## Contribution Workflow

1. Find or create the issue for your change.
2. Update your local `dev` branch.
3. Create a new branch from `dev`.
4. Make the change.
5. Add or update tests and documentation when needed.
6. Run the relevant checks locally.
7. Open a pull request targeting `dev`.
8. Link the related issue in the pull request description.

## Reporting Bugs

When reporting a bug, include:

- The installed version or commit hash.
- Your Python version.
- Your operating system.
- The relevant Quart, python-socketio, and server versions when possible.
- A minimal code example or reproduction steps.
- What you expected to happen.
- What happened instead.
- Any traceback, logs, or error messages.

The more focused the reproduction is, the easier it is to confirm and fix the
bug.

## Suggesting Features

Feature requests should start as issues before any branch is created.

When suggesting a feature, describe:

- The problem or use case.
- Why it belongs in Quart-SocketIo.
- What the proposed API or behavior might look like.
- Any compatibility concerns with Quart, python-socketio, or existing helpers.

Large features should be discussed before implementation so the final pull
request stays focused and reviewable.

## Pull Requests

Pull requests should include:

- A clear summary of the change.
- A link to the related issue.
- Notes about tests or checks that were run.
- Documentation updates when user-facing behavior changes.
- Any migration notes when behavior changes in a meaningful way.

Pull requests that are not linked to an issue, or that are based on a branch
other than `dev`, may be asked to update their workflow before review.

## Code Style

The project uses Ruff for formatting and linting.

Before opening a pull request, run:

```bash
uv run ruff format .
uv run ruff check .
```

The project also uses Pyright for type checking:

```bash
uv run pyright
```

Prefer small, explicit changes that match the existing code style. Avoid adding
new abstractions unless they simplify real duplication or clarify behavior.

## Tests

Run the test suite with:

```bash
uv run pytest
```

For behavior changes, add tests that demonstrate the new or fixed behavior.
For bug fixes, include a regression test when possible.

## Documentation

Documentation lives in `docs/` and is built with MkDocs.

Documentation contributions are welcome. You can help by fixing typos,
improving explanations, adding examples, updating outdated instructions, or
expanding the English and Brazilian Portuguese pages.

Update the documentation when you change:

- Public API behavior.
- Configuration options.
- Installation or development instructions.
- Event, namespace, room, or deployment behavior.

When adding or changing documentation, keep the English page and the matching
`pt-BR` page aligned whenever both versions exist. For example, changes to
`docs/configuration.md` should also be reflected in
`docs/configuration.pt-BR.md`.

Run the documentation build before submitting documentation changes:

```bash
uv run mkdocs build --strict
```

## Security

If you believe you have found a security vulnerability, do not open a public
issue. Follow the instructions in `SECURITY.md` so the report can be handled
privately.

## Review Process

Maintainers review pull requests for correctness, compatibility, test coverage,
documentation, and fit with the project goals.

You may be asked to make changes before a pull request is merged. Please keep
the branch up to date with `dev` while review is in progress.
