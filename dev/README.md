# Development CLI

Repository-local maintenance commands live under `dev/cli`.

Run the command group from the repo root with:

```shell
uv run python -m dev.cli --help
```

Common commands:

```shell
uv run python -m dev.cli docs build
uv run python -m dev.cli docs dev
uv run python -m dev.cli ai skill-ref
uv run python -m dev.cli build
uv run python -m dev.cli release-check
uv run python -m dev.cli publish
```

Notes:

- `docs ...` uses the `docs` dependency group automatically.
- `build` refreshes packaged AI skill references, rebuilds `dist/`, builds docs, runs `uv build`, then validates the built distributions.
- `release-check` runs the local release gate: tests, lint, type check, docs build, package build, metadata validation, and install smoke tests.
- `publish` runs `build` first, then `uv publish`.

## Release checklist

Before publishing:

1. Bump the version in `pyproject.toml` and `uv.lock`.
2. Update `CHANGELOG.md`.
3. Run:

   ```shell
   uv run python -m dev.cli release-check
   ```

4. Confirm PyPI credentials or trusted publishing are configured.
5. Publish:

   ```shell
   uv run python -m dev.cli publish
   ```
