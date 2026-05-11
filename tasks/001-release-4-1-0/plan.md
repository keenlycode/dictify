# Plan

1. Prepare release metadata.
   - Update `pyproject.toml` to `4.1.0`.
   - Update `uv.lock` project metadata to `4.1.0`.
   - Add `CHANGELOG.md` entry.

2. Validate release artifacts.
   - Run `uv run python -m dev.cli release-check`.
   - Confirm `dist/dictify-4.1.0.tar.gz` and `dist/dictify-4.1.0-py3-none-any.whl` are built.

3. Commit and tag.
   - Commit current release changes.
   - Create git tag `v4.1.0` on the release commit.

4. Publish package.
   - Run `uv run python -m dev.cli publish`.
   - Verify PyPI exposes `dictify==4.1.0`.

5. Publish docs.
   - Run docs publish for version `4.1.0` and alias `latest`.
   - Verify public docs resolve to the new version.
