# Python 3.11 Runtime Support

Owner: Milin
State: doing

## Goal

Make Dictify installable and importable on Python 3.11 and Python >=3.12, especially for Raspberry Pi Zero use, while preserving the public annotation-based API.

## Scope

- Lower package runtime requirement from Python 3.12 to Python 3.11.
- Replace internal Python 3.12-only syntax with Python 3.11-compatible typing forms.
- Keep `typing.Annotated[...]` public API support intact.
- Update relevant docs and lock metadata.
- Validate with repo-local test/lint/type/build checks where practical.

## Constraints

- Keep changes minimal and readable.
- Do not remove annotation-first Dictify examples or behavior.
- Do not publish, commit, or change release version unless explicitly requested.

## Release Version

- User requested version bump to `5.0.1` after Python 3.11 support changes.
