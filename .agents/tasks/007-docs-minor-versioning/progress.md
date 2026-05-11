# Progress

State: done

## Current Status

Published the current docs as `4.1.x`, set `latest` to `4.1.x`, and removed old exact `4.1.1` and `4.1.0` docs entries.

## Recent Changes

- Added docs-version normalization in `dev/cli/docs.py`.
- Added focused tests for patch-to-minor-line docs labels.
- Documented the policy in `dev/README.md` and linked to it from `README.md`.
- Ran focused tests, Ruff, and `uv run python -m dev.cli release-check` successfully.
- Pushed commit `79989b5` to `origin/main`.
- Published docs with `uv run python -m dev.cli docs publish 4.1.1 latest`; the command deployed `4.1.x`.
- Removed the old exact docs entry with `uv run --group docs mike delete --push --branch docs 4.1.1`.
- Verified the remote docs branch `versions.json` lists `4.1.x` and not `4.1.1`.
- Verified cache-busted public `versions.json` lists `4.1.x` and not `4.1.1`.
- Verified `https://keenlycode.github.io/dictify/4.1.x/` and `https://keenlycode.github.io/dictify/latest/` return 200.
- Verified `https://keenlycode.github.io/dictify/4.1.1/` returns 404 with cache busting.
- Removed the old exact docs entry with `uv run --group docs mike delete --push --branch docs 4.1.0`.
- Verified the remote docs branch `versions.json` lists `4.1.x` and not `4.1.0`.
- Verified the remote docs branch no longer has a `4.1.0` directory.
- Observed GitHub Pages still serving cached public `4.1.0` content immediately after deletion; the docs branch state is correct.

## Next Step

No further action.
