---
name: dictify-development
description: Use when developing, debugging, testing, documenting, building, releasing, or changing development workflow in the Dictify repository. Always inspect dev/cli to understand the repo-local workflow before choosing commands.
---

# Dictify Development

## First Step

Before changing code, docs, build behavior, release flow, or validation commands, inspect the development workflow:

- Read `dev/README.md` for the command summary.
- Read the relevant module under `dev/cli/` before running or changing a workflow command.
- Prefer repository-local commands exposed by `uv run python -m dev.cli ...` over ad hoc command sequences.

## Repository Map

- Package code: `src/dictify/`
- Tests: `tests/`
- Docs source: `docs-src/`
- MkDocs overrides: `docs-src/overrides/`
- Generated packaged AI skill references: `src/dictify/ai_skills/dictify-usage/references/`
- Development CLI: `dev/cli/`

## Common Commands

Use these from the repo root after checking `dev/cli` for current behavior:

```shell
uv run python -m dev.cli ai skill-ref
uv run python -m dev.cli ai skill-ref --check
uv run python -m dev.cli docs build
uv run python -m dev.cli docs dev
uv run python -m dev.cli build
uv run python -m dev.cli release-check
```

For focused local checks, prefer the configured tools:

```shell
uv run pytest
uv run ruff check src tests dev
uv run ty check
```

## Working Rules

- Edit `docs-src/` for documentation source; regenerate packaged AI skill references with `dev.cli ai skill-ref`.
- Do not directly edit generated AI skill references unless the task explicitly concerns generated output.
- Run `dev.cli ai skill-ref --check` after documentation changes that should sync into the packaged skill.
- Use `dev.cli release-check` as the release gate when preparing to publish.
- Do not publish, push docs, or change release versions unless explicitly requested.
- Preserve direct annotation-first Dictify examples, such as `email: str = Field(required=True)`.
