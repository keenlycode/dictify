---
name: dictify-usage
description: Use Dictify correctly in this repository for standalone field validation and annotation-first mapping models. Use when writing code, tests, docs, or examples that should validate Python mappings or JSON-like documents with `Field`, `Model`, `ListOf`, or `UNDEF`.
---

# Dictify Usage

## Goal

Use Dictify in the way this repository documents and tests today. Prefer the public API and preserve established behavior.

## Workflow

1. Read the skill references first:
   - `references/index.md`
   - `references/usage.md`
   - `references/field-api.md`
   - `references/validation-recipes.md`
2. If behavior is still unclear, read `tests/test_dictify.py` and the package code under `src/dictify/`.
3. Prefer the public import surface:
   - Use `from dictify import Field, Model, ListOf, UNDEF`
   - Do not use private module imports in user-facing examples unless the task is explicitly about internals
4. Choose the smallest fitting abstraction:
   - Use standalone `Field(...)` for single-value validation
   - Use `Model` for mapping-shaped documents
   - Use `ListOf` only when working with validated list values returned by Dictify
5. Follow current model style:
   - Prefer annotation-first declarations such as `email: str = Field(required=True)`
   - Use `Field(...)` for defaults, required fields, and extra validators
   - Preserve both attribute access and mapping access semantics
6. Respect current limitations:
   - Static type checker support for `email: str = Field(...)` is still limited and may require `cast(Any, Field(...))`
   - `model.dict()` returns native Python structures but does not serialize `datetime` automatically for JSON
7. Reuse field definitions carefully:
   - `User.email` returns the shared class-level `Field` definition
   - Prefer `User.email.clone()` when using a model field as a standalone validator outside the model
8. Verify with project-local commands when code changes:
   - `uv run pytest`
   - `uv run ruff check src tests`
   - `uv run ty check`

## Preferred Patterns

### Standalone field

```python
from dictify import Field

email = Field(required=True).instance(str).match(r".+@.+")
email.value = "user@example.com"
```

### Annotation-first model

```python
from typing import Any, cast

from dictify import Field, Model


class User(Model):
    email: str = cast(Any, Field(required=True).match(r".+@.+"))
```

### Nested mapping model

```python
from typing import Any, cast

from dictify import Field, Model


class User(Model):
    name: str = cast(Any, Field(required=True))


class Note(Model):
    title: str = cast(Any, Field(required=True))
    user: User = cast(Any, Field(required=True))
```

## Avoid

- Do not describe Dictify by comparing it to other validation libraries
- Do not assume automatic JSON serialization of `datetime`
- Do not treat `User.email` as isolated instance state
- Do not import from private modules in user-facing examples
