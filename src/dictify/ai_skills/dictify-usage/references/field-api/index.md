<!-- Generated from script, do not edit directly. -->

# Field API

`dictify.Field()` creates a reusable validator object.

```python
Field(
    required: bool = False,
    default: Any = UNDEF,
    grant: list[Any] | None = None,
)
```

For `Model` classes, prefer `Annotated[..., Field(...)]` for type-checker-friendly field declarations:

```python
from typing import Annotated

from dictify import Field, Model


class User(Model):
    email: Annotated[str, Field(required=True)]
```

Use `Field(...)` to add options, standalone state, and validation methods.

## Pages

- [Field Options](options.md): `required`, `default`, `grant`, and model field typing.
- [Field Validators](validators.md): `instance()`, `listof()`, `match()`, `search()`, `model()`, `verify()`, and `func()`.
- [Field State](state.md): `value`, `reset()`, `default`, `has_default`, `validate()`, and `clone()`.
- [ListOf](listof.md): list values returned by `Field.listof(...)`.
