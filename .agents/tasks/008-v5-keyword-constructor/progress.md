# Progress

State: done

Current status: v5 dev work now includes Cyclopts-compatible model introspection and passes validation.

Recent changes:
- Created task state for v5 keyword constructor work.
- Updated `Model.__init__` to support mapping input plus keyword field data, with `_strict` as keyword-only config.
- Made the initial mapping argument positional-only so `data` can be used as a model field keyword.
- Updated tests for keyword construction, duplicate override behavior, `_strict`, and `strict`/`data` model fields.
- Bumped package metadata to `5.0.0.dev0` and updated docs/changelog drafts for planned `5.0.0`.
- Refreshed packaged AI skill references from `docs-src/`.
- Final review found and fixed stale `dev/README.md` docs-version examples.
- Validation passed: focused tests, all tests, Ruff, AI skill reference check, MkDocs build, and full `dev.cli release-check`.
- Reopened task to explore Cyclopts behavior before final `5.0.0` release.
- Confirmed Cyclopts sees the generic `Model.__init__` shape without extra signature support and cannot infer nested field options.
- Added generated per-subclass constructor signatures on both the class and subclass `__init__` wrapper.
- Verified Cyclopts can parse nested options such as `--data.name name --data.lname lname` into a Dictify model.
- Fixed eager-annotation model registration for Python 3.14 annotation behavior by using `inspect.get_annotations()` for class-local annotation keys.
- Updated docs/changelog and regenerated packaged skill references.
- Validation passed: all tests, Ruff, AI skill reference check, and full `dev.cli release-check`.

Next steps:
- Commit the new Cyclopts/introspection follow-up changes when ready.

Blockers: none.
