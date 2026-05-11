<!-- Generated from script, do not edit directly. -->

# Field State

`Field` stores its own value, so it can be used directly outside of a model.

## `value`

Read or assign the standalone field value. Assignment validates the value and
stores transformed values returned by `func(...)` or `model(...)`.

```python
from dictify import Field

field = Field(required=True).instance(str)

field.value = "hello"
assert field.value == "hello"
```

Reading `value` from a required field before assignment raises
`Field.RequiredError`. Failed assignments raise `Field.VerifyError` and leave
the previous value unchanged.

## `reset()`

Reset `value` to the configured default. If there is no default, reset it to
`UNDEF`.

```python
field = Field(default="draft")
field.value = "hello"
field.reset()

assert field.value == "draft"
```

## `default`

Return the materialized default value. If the field was configured with a
default factory, the factory is called each time `default` is read.

```python
from datetime import UTC, datetime

created_at = Field(default=lambda: datetime.now(UTC))
assert isinstance(created_at.default, datetime)
```

`get_default()` is kept as a compatibility alias for `default`.

## `has_default`

Return whether the field was configured with a default. `None` counts as a
configured default.

```python
required_name = Field(required=True)
optional_note = Field(default=None)

assert required_name.has_default is False
assert optional_note.has_default is True
```

## `validate(value)`

Validate a value without assigning it to the field. The returned value is the
final value after runtime type checks and validator transformations.

```python
field = Field().instance(str).func(str.upper)
assert field.validate("draft") == "DRAFT"
```

## `clone()`

Create a fresh field with the same validation definition and independent
standalone state.

```python
email = Field(required=True).instance(str).match(r".+@.+")
other_email = email.clone()
```

When a `Field` is declared on a `Model` class, that class attribute acts as a shared schema definition. Individual model instances keep their runtime values separately.
