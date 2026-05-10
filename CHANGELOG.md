# Changelog

## 4.0.2

- Clarified `Field.verify()` and `Field.func()` behavior in docs and docstrings.
- Made validation errors explicit and allowed `Field.func()` to transform stored values.
- Added release validation and CI checks so package builds are ready for PyPI publishing.

## 4.0.1

- Added a packaged `dictify-usage` AI skill under `src/dictify/ai_skills/`.
- Added `dictify ai-skill-install` to install the packaged skill into an agent skill directory.
- Added repository-local development commands under `dev/cli` for docs builds, AI skill reference sync, package builds, and publishing.

## 4.0.0

- `Model` now behaves as a `MutableMapping` instead of subclassing `dict`.
- Model fields are now annotation-first: `name: str = Field(...)` is the preferred declaration style.
- Declared model fields support descriptor-style attribute access alongside mapping access.
- Undeclared public attributes now follow `strict` in the same way as undeclared keys.
- The minimum supported Python version is now `3.12`.
- Runtime support for annotated `Field(...)` model declarations is complete. Static type checker support may vary, but direct annotation-first declarations are the canonical Dictify style.
