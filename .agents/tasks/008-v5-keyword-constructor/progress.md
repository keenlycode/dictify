# Progress

State: done

Current status: v5 keyword constructor implementation, docs, generated skill references, and validation are complete. Package metadata now uses the development version `5.0.0.dev0` until release.

Recent changes:
- Created task state for v5 keyword constructor work.
- Updated `Model.__init__` to support mapping input plus keyword field data, with `_strict` as keyword-only config.
- Made the initial mapping argument positional-only so `data` can be used as a model field keyword.
- Updated tests for keyword construction, duplicate override behavior, `_strict`, and `strict`/`data` model fields.
- Bumped package metadata to `5.0.0.dev0` and updated docs/changelog drafts for planned `5.0.0`.
- Refreshed packaged AI skill references from `docs-src/`.
- Final review found and fixed stale `dev/README.md` docs-version examples.
- Validation passed: focused tests, all tests, Ruff, AI skill reference check, MkDocs build, and full `dev.cli release-check`.

Next steps:
- Optional follow-up: test whether Cyclopts needs generated `__signature__` support for deeper model introspection.

Blockers: none.
