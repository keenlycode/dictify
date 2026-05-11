# Release 4.1.0

## Goal

Prepare, validate, tag, publish, and document the Dictify `4.1.0` release.

## Scope

- Release metadata and changelog for `4.1.0`.
- Existing code/docs changes for `Annotated[..., Field(...)]` support and usage docs split.
- Package publication to PyPI.
- Git tag creation for the release.
- Versioned docs publication with `latest` alias.

## Constraints

- Do not publish, push docs, or create release tags without explicit user confirmation.
- Use repository-local workflow commands from `dev.cli`.
- Keep generated AI skill references synced from `docs-src`.

## Expected Outcome

- A committed release state for `4.1.0`.
- Git tag `v4.1.0`.
- Published PyPI package `dictify==4.1.0`.
- Published docs for `4.1.0` with the `latest` alias.
