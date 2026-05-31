# Changelog

## 5.0.1

- Restored install/runtime support for Python 3.11 while keeping annotation-first model declarations.

## 5.0.0

- Added keyword-data model construction, such as `User(name="Ada")`, alongside mapping input.
- Replaced the `strict=` constructor option with `_strict=` so `strict` can be used as normal model data.
- Added inspectable model constructor signatures for tools such as Cyclopts.
- Documented mapping input for JSON-like data and keyword input for Python object-style construction.

## 4.1.1

- Restructured documentation source paths to mirror the public navigation.
- Updated packaged AI skill references to use the same nested guide structure.
- Simplified the packaged `dictify-usage` skill so it is concise and portable in installed Python environments.

## 4.1.0

- Added type-checker-friendly `Annotated[..., Field(...)]` model field declarations.
- Documented direct assignment declarations as a runtime-supported compatibility style.
- Split Usage documentation into focused pages for overview, model behavior, declaration styles, and partial validation.
- Documented `Field.has_default` for checking whether a field has a configured default.
- Updated packaged AI skill reference generation to copy nested guide markdown from `docs-src/guide/**/*.md`.

## 4.0.4

- Split Field API documentation into focused pages for options, validators, state, and `ListOf`.
- Made `Field.default` the primary implementation for materialized defaults while keeping `get_default()` as a compatibility alias.
- Updated the AI skill install default path to `.agents/skills/dictify-usage`.

## 4.0.3

- Refreshed packaged AI skill guidance to prefer direct annotation-first model declarations.
- Simplified AI skill reference sync to copy guide documentation from `docs-src/guide/`.
- Moved the AI skill docs page and MkDocs overrides under `docs-src/`.

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
