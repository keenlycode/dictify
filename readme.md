# Dictify

Schema and data validation for Python mappings and JSON-like documents.

`dictify` is a lightweight library for defining field-level validation and composing those fields into mapping-shaped models.

- Use `Field(...)` for standalone validation.
- Use `Model` for named fields, nested structures, and strict key handling.
- Convert model data explicitly with `dict(model)` or `model.dict()`.

## Install

```shell
pip install dictify
```

## Quick Example

```python
from datetime import datetime

from dictify import Field, Model


class Note(Model):
    title = Field(required=True).instance(str).verify(
        lambda value: len(value) <= 300,
        "Title must be 300 characters or fewer",
    )
    content = Field().instance(str)
    timestamp = Field(
        required=True,
        default=lambda: datetime.utcnow().isoformat(),
    ).func(datetime.fromisoformat)


note = Note({"title": "Dictify", "content": "dictify is easy"})

note["content"] = "Updated content"
note.update({"content": "Updated again"})

# These raise Model.Error.
note["title"] = 0
note.update({"title": 0})
```

## Native Conversion

`Model` behaves like a mutable mapping, but explicit conversion is preferred when you need plain Python data.

```python
import json

note_dict = dict(note)        # shallow mapping conversion
note_native = note.dict()     # recursive dict/list conversion
note_json = json.dumps(note.dict())
```

## Why Dictify

- Small API surface centered around `Field` and `Model`
- Validation happens on assignment, not only at construction time
- Works for standalone values and nested document structures
- Supports defaults, required fields, regex checks, custom functions, and list/model coercion

## Documentation

- Docs: https://nitipit.github.io/dictify/
- Usage: https://nitipit.github.io/dictify/guide/usage/
- Field API: https://nitipit.github.io/dictify/guide/field-api/
- Validation Recipes: https://nitipit.github.io/dictify/guide/validation-recipes/
