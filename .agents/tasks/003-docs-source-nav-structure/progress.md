# Progress

State: done

## Current Status

Docs source now mirrors the MkDocs navigation, packaged AI skill references are regenerated, and validation passed.

## Recent Changes

- Defined scope, plan, and checklist.
- Moved `validation-recipes.md` to `validation-recipes/index.md`.
- Moved Field API pages under `field-api/`.
- Updated MkDocs nav, homepage guide links, AI skill guidance, and smoke validation paths.
- Regenerated nested packaged references under `src/dictify/ai_skills/dictify-usage/references/`.
- Validation passed with `uv run python -m dev.cli ai skill-ref --check`.
- Validation passed with `uv run python -m dev.cli docs build`.
- Validation passed with `uv run ruff check dev src tests`.

## Next Steps

- None.

## Blockers

- None.
