# v5 Keyword Constructor

Goal: prepare Dictify 5.0.0 with keyword-based model construction while preserving mapping input for JSON-like data.

Scope:
- Add `Model(..., _strict=...)` config and remove `strict=` constructor config.
- Add keyword field input via `**kwargs`.
- Keep mapping input as supported canonical JSON/dict path.
- Bump version to `5.0.0`.
- Update tests, docs, and changelog for the breaking change.

Decisions:
- Use `_strict`, not `__strict`.
- `strict` should become available as a normal model field keyword.
- If both mapping and keyword data provide the same key, keyword data overrides mapping data.
- Generated constructor signatures / deeper Cyclopts introspection are follow-up work, not in this task.

Owner: primary project agent.
