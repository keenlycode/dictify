# Plan

1. Inspect current version/changelog/docs references to `strict` and model construction.
2. Update `Model.__init__` to accept `data=None`, keyword-only `_strict=True`, and `**kwargs`.
3. Add/update tests for keyword construction, `_strict`, duplicate override behavior, and `strict` as data.
4. Bump version to `5.0.0` in project metadata and lockfile if needed.
5. Update docs/changelog/examples to use `_strict` and mention the v5 breaking change.
6. Validate with focused tests and relevant repo checks.
7. Final review/iteration: inspect diffs and rerun/fix validation as needed.
