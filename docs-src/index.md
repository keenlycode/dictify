<section class="home-hero">
  <div class="home-hero__content">
    <h1 class="home-hero__title">Dictify</h1>
    <p class="home-hero__lead">Lightweight validation for Python mappings and JSON-like documents.</p>
    <p class="home-hero__lead"><code>dictify</code> is a lightweight validation library for standalone fields and mapping-shaped models. It is designed for small schema layers, partial validation, and annotation-first models with explicit dict-like behavior.</p>
    <ul class="home-hero__list">
      <li>Python <code>3.12+</code></li>
      <li>Use <code>Field(...)</code> for defaults, required fields, and extra validators</li>
      <li>Use Python annotations to declare <code>Model</code> field types</li>
      <li>Access model data with either attributes or mapping syntax</li>
    </ul>
  </div>
</section>

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
```

Create and update validated data:

```python
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

## Guides

- [Usage](guide/usage.md)
- [Field API](guide/field-api.md)
- [Validation Recipes](guide/validation-recipes.md)
