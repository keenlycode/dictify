# Plan

1. Fetch open Dependabot alerts from GitHub.
2. Map each alert to `pyproject.toml`, `uv.lock`, or another manifest if present.
3. Update affected dependencies with targeted `uv lock --upgrade-package ...` where possible.
4. Run validation, preferring `uv run python -m dev.cli release-check`.
5. Commit repository changes and report whether a package release is needed.
