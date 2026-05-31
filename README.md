# Dictify

Lightweight validation for Python mappings and JSON-like documents.

Dictify provides standalone field validation and annotation-first `Model` classes for dict-shaped data. It keeps mapping access and attribute access together, validates assignments, supports strict or permissive unknown-key handling, and converts models back to plain Python data.

- Python `3.11+`
- `Field(...)` for defaults, required fields, and validators
- `Model` for mapping-shaped schemas
- `dict(model)` for shallow conversion, `model.dict()` for recursive conversion
- Inspectable model signatures for CLI/data-binding tools such as Cyclopts

## Install

```shell
pip install dictify
```

## Example

```python
from datetime import UTC, datetime
from typing import Annotated

from dictify import Field, Model


class Note(Model):
    title: Annotated[
        str,
        Field(required=True).verify(
            lambda value: len(value) <= 300,
            "Title must be 300 characters or fewer",
        ),
    ]
    content: Annotated[str, Field()]
    timestamp: Annotated[datetime, Field(default=lambda: datetime.now(UTC))]


note = Note(title="Dictify", content="dictify is easy")

note.content = "Updated content"
note["content"] = "Updated again"

assert note["content"] == "Updated again"
assert isinstance(note.dict()["timestamp"], datetime)
```

`Model` is strict by default. Pass `_strict=False` to keep undeclared keys as extra model data:

```python
note = Note({"title": "Dictify"}, _strict=False)
note.category = "docs"

assert note["category"] == "docs"
```

Standalone fields work without a model:

```python
email = Field(required=True).instance(str).match(r".+@.+")
email.value = "user@example.com"
```

## AI Skill

Dictify ships with an optional packaged AI skill installer:

```shell
dictify ai-skill-install
```

## Development

Repository-local maintenance commands live under `dev/cli`:

```shell
uv run python -m dev.cli --help
uv run python -m dev.cli release-check
```

See [`dev/README.md`](dev/README.md) for the command summary and release workflow.

## Documentation

- Docs: https://keenlycode.github.io/dictify/
- Changelog: https://github.com/keenlycode/dictify/blob/main/CHANGELOG.md
