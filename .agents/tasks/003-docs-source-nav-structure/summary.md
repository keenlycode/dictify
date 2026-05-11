# Docs Source Nav Structure

## Goal

Restructure `docs-src/guide/` so source paths mirror the MkDocs navigation.

## Scope

- Move Validation Recipes into `docs-src/guide/validation-recipes/index.md`.
- Move Field API pages into `docs-src/guide/field-api/`.
- Update MkDocs navigation and markdown links.
- Regenerate packaged AI skill references.
- Validate docs and generated references.

## Constraints

- Keep public navigation labels unchanged.
- Preserve the existing documentation content unless path changes require link edits.
- Use repository-local `dev.cli` commands for validation.
