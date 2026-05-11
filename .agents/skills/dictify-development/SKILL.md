---
name: dictify-development
description: Use when developing, debugging, testing, documenting, building, releasing, or changing development workflow in the Dictify repository. Always inspect dev/cli to understand the repo-local workflow before choosing commands.
---

# Dictify Development

## First Step

Before changing code, docs, build behavior, release flow, or validation commands:

1. Read `dev/README.md`.
2. Inspect the relevant implementation under `dev/cli/`.
3. Prefer repository-local commands exposed by `uv run python -m dev.cli ...`.

Treat `dev/README.md` and `dev/cli/` as the source of truth for workflow details.

## Working Rules

- Edit `docs-src/` for documentation source; regenerate packaged AI skill references with `dev.cli ai skill-ref`.
- Do not directly edit generated AI skill references unless the task explicitly concerns generated output.
- Run `dev.cli ai skill-ref --check` after documentation changes that should sync into the packaged skill.
- Use `dev.cli release-check` as the release gate when preparing to publish.
- Do not publish, push docs, or change release versions unless explicitly requested.
- Preserve direct annotation-first Dictify examples, such as `email: str = Field(required=True)`.
