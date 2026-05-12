# Dictify

Lightweight validation for Python mappings and JSON-like documents.

`dictify` is a lightweight validation library for standalone fields and mapping-shaped models.

It is designed for small schema layers, partial validation, and annotation-first models with explicit dict-like behavior.

- Python `3.12+`
- Use `Field(...)` for defaults, required fields, and extra validators
- Use Python annotations to declare `Model` field types
- Access model data with either attributes or mapping syntax

## Why Dictify?

- Validate a single value with `Field(...)` without defining a full model
- Define annotation-first `Model` classes for dict-shaped documents
- Keep mapping access and attribute access together
- Handle unknown keys and public attributes explicitly with `_strict`
- Convert back to plain Python data with `dict(model)` and `model.dict()`

## Install

```shell
pip install dictify
```

## Quick Example

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
    timestamp: Annotated[
        datetime,
        "creation time",
        Field(default=lambda: datetime.now(UTC)),
    ]


note = Note(title="Dictify", content="dictify is easy")

note.content = "Updated content"
note["content"] = "Updated again"

# These raise Model.Error.
note.title = 0
note["title"] = 0
```

## Strict Mode

`Model` is strict by default.

- `_strict=True` rejects undeclared keys and undeclared public attributes
- `_strict=False` stores undeclared keys and attributes as extra model data

```python
note = Note({"title": "Dictify"}, _strict=False)

note.category = "docs"
assert note["category"] == "docs"
assert dict(note)["category"] == "docs"
```

## Native Conversion

Use explicit conversion when you need plain Python data.

```python
import json

note_dict = dict(note)        # shallow dict conversion
note_native = note.dict()     # recursive dict/list conversion
note_json = json.dumps(note.dict())
```

## Standalone Fields

`Field.instance(...)` still works well for standalone validation.

```python
email = Field(required=True).instance(str).match(r".+@.+")
email.value = "user@example.com"
```

## AI Skill

`dictify` ships with an installed CLI for the packaged AI skill.

```shell
dictify ai-skill-install
```

The installer prompts for the exact destination folder and defaults to:

```text
.agents/skills/dictify-usage
```

If the destination already exists, `dictify` asks before overwriting it.

## Development CLI

Repository-local maintenance commands live under `dev/cli`.

Run them from the repo root with:

```shell
uv run python -m dev.cli --help
```

Examples:

```shell
uv run python -m dev.cli docs build
uv run python -m dev.cli docs dev
uv run python -m dev.cli ai skill-ref
uv run python -m dev.cli build
uv run python -m dev.cli release-check
```

See [`dev/README.md`](dev/README.md) for the command summary and docs versioning policy.

## Typing Status

The annotation-first model API is fully supported at runtime.

For static type checkers, prefer `Annotated[str, Field(...)]` without assigning `Field(...)` as the class value. Declarations like `email: str = Field(...)` remain supported at runtime, but static type checker support for that assignment style may vary.

## Documentation

- Docs: https://keenlycode.github.io/dictify/
- Usage: https://keenlycode.github.io/dictify/guide/usage/
- AI Skill: https://keenlycode.github.io/dictify/ai-skill/
- Field API: https://keenlycode.github.io/dictify/guide/field-api/
- Validation Recipes: https://keenlycode.github.io/dictify/guide/validation-recipes/
- Changelog: https://github.com/keenlycode/dictify/blob/main/CHANGELOG.md
