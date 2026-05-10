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

For `Model` classes, prefer Python annotations for the base field type:

```python
from dictify import Field, Model


class User(Model):
    email: str = Field(required=True)
```

Use `Field(...)` to add options, standalone state, and validation methods.

## Pages

- [Field Options](field-options.md): `required`, `default`, `grant`, and model field typing.
- [Field Validators](field-validators.md): `instance()`, `listof()`, `match()`, `search()`, `model()`, `verify()`, and `func()`.
- [Field State](field-state.md): `value`, `reset()`, `default`, `validate()`, and `clone()`.
- [ListOf](listof.md): list values returned by `Field.listof(...)`.
