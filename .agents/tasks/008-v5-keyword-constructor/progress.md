# Progress

State: done

Current status: Dictify 5.0.0 is merged, tagged, pushed, published to PyPI, and docs are published.

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
- Reopened task to document CLI / AI agent input schema use as a core v5 feature.
- Added `guide/usage/cli-inputs.md` with signature, Cyclopts, and AI-agent CLI input examples.
- Added the new page to MkDocs navigation and Usage index.
- Updated README feature bullets and linked the model behavior page to the dedicated CLI inputs guide.
- Regenerated packaged AI skill references, including the new CLI inputs reference.
- Validation passed: AI skill reference check, MkDocs build, and full pytest suite.
- Bumped package metadata from `5.0.0.dev0` to final `5.0.0` and updated `uv.lock`.
- Validation passed on `v5-dev` and again after merging to `main`: `uv run python -m dev.cli release-check`.
- Merged `v5-dev` to `main` with merge commit `1f556a0` and tagged `v5.0.0`.
- Pushed `main` and `v5.0.0` to origin.
- Published `dictify==5.0.0` to PyPI and verified the PyPI release JSON.
- Published versioned docs for `5.0.x` with `latest` pointing to the 5.0 docs line.

Next steps:
- None.

Blockers: none.
