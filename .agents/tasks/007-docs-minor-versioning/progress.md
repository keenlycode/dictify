# Progress

State: doing

## Current Status

Implemented the local docs publishing policy. Exact patch versions passed to `dev.cli docs publish`, such as `4.1.1`, now publish under their minor docs line, such as `4.1.x`.

## Recent Changes

- Added docs-version normalization in `dev/cli/docs.py`.
- Added focused tests for patch-to-minor-line docs labels.
- Documented the policy in `dev/README.md` and linked to it from `README.md`.
- Ran focused tests, Ruff, and `uv run python -m dev.cli release-check` successfully.

## Next Step

Wait for explicit confirmation before publishing `4.1.x` docs or changing old exact docs entries.
