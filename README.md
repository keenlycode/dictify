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
- Handle unknown keys and public attributes explicitly with `strict`
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
    title: str = Field(required=True).verify(
        lambda value: len(value) <= 300,
        "Title must be 300 characters or fewer",
    )
    content: str = Field()
    timestamp: Annotated[datetime, "creation time"] = Field(
        default=lambda: datetime.now(UTC)
    )


note = Note({"title": "Dictify", "content": "dictify is easy"})

note.content = "Updated content"
note["content"] = "Updated again"

# These raise Model.Error.
note.title = 0
note["title"] = 0
```

## Strict Mode

`Model` is strict by default.

- `strict=True` rejects undeclared keys and undeclared public attributes
- `strict=False` stores undeclared keys and attributes as extra model data

```python
note = Note({"title": "Dictify"}, strict=False)

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
./.agents/skills/dictify-usage
```

If the destination already exists, `dictify` asks before overwriting it.

## Typing Status

The annotation-first model API is fully supported at runtime.

Static type checker support for declarations like `email: str = Field(...)` is still limited and may require `cast(Any, Field(...))` depending on the checker and editor.

## Documentation

- Docs: https://nitipit.github.io/dictify/
- Usage: https://nitipit.github.io/dictify/guide/usage/
- AI Skill: https://nitipit.github.io/dictify/guide/ai-skill/
- Field API: https://nitipit.github.io/dictify/guide/field-api/
- Validation Recipes: https://nitipit.github.io/dictify/guide/validation-recipes/
- Changelog: https://github.com/nitipit/dictify/blob/dev/CHANGELOG.md
