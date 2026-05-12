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
uv run python -m dev.cli docs publish 5.0.0 latest
uv run python -m dev.cli ai skill-ref
uv run python -m dev.cli build
uv run python -m dev.cli release-check
uv run python -m dev.cli publish
```

Notes:

- `docs ...` uses the `docs` dependency group automatically.
- `docs publish <version> <alias>` publishes patch versions under their minor docs line. For example, `5.0.0` deploys as `5.0.x`, and `latest` points to that docs line.
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

## Documentation versioning

Package versions and git tags stay exact, such as `5.0.0` and `v5.0.0`.
Published docs are grouped by minor release line, such as `5.0.x`.

For a patch release, publish docs only when the docs changed or the patch changes documented behavior:

```shell
uv run python -m dev.cli docs publish 5.0.0 latest
```

The docs command deploys that example as `5.0.x` and sets `latest` to the same docs line.
