# Dictify

Schema and data validation for Python mappings and JSON-like documents.

`dictify` is a lightweight library for standalone field validation and mapping-shaped models with annotated fields.

- Python `3.12+`
- Use `Field(...)` for defaults, required fields, and extra validators
- Use Python annotations to declare `Model` field types
- Access model data with either attributes or mapping syntax

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

## Documentation

- Docs: https://nitipit.github.io/dictify/
- Usage: https://nitipit.github.io/dictify/guide/usage/
- Field API: https://nitipit.github.io/dictify/guide/field-api/
- Validation Recipes: https://nitipit.github.io/dictify/guide/validation-recipes/
