<!-- Generated from script, do not edit directly. -->

# Field API

## `Field()`

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
class User(Model):
    email: str = Field(required=True)
```

Use `Field(...)` to add options and extra validators.

## Required Fields

Set `required=True` when a value must be present.

Required fields raise `Field.RequiredError` when:

1. You read `field.value` before assigning a valid value.
2. You create a `Model` without providing the required field.
3. You delete a required field from a model.

## Default Values

Defaults can be static values or factories.

```python
from datetime import UTC, datetime
import uuid

Field(default=0)
Field(default=uuid.uuid4)
Field(default=lambda: datetime.now(UTC))
```

Defaults are applied when:

1. A standalone `Field` is created.
2. `Field.reset()` is called.
3. A `Model` is created without a value for that field.
4. A model field with a default is deleted.

## Granted Values

Granted values always pass validation, even if later validators would reject them.

```python
field = Field(grant=[None]).instance(str)
field.value = None
```

## Model Field Typing

Model field types come from annotations.

```python
from typing import Annotated


class User(Model):
    email: Annotated[str, "primary email"] = Field(required=True).match(r".+@.+")
    age: int | None = Field(default=None)
```

`Annotated[...]` metadata is ignored for runtime typing unless it contains a `Field(...)`, which is rejected as ambiguous when the class attribute is also assigned to `Field(...)`.

## Validation Methods

Field validators can be chained.

```python
username = Field(required=True).instance(str).match(r"[a-zA-Z0-9 ._-]+$")
```

### `instance(type_)`

Verify that the assigned value is an instance of the given type.

For `Model` fields, prefer annotations for the base type. `instance(...)` remains useful for standalone `Field` validation and compatibility.

```python
email = Field().instance(str)
email.value = "user@example.com"

number = Field().instance((int, float))
number.value = 0
number.value = 0.1
```

### `listof(type_=UNDEF, validate=None)`

Validate that the value is a list, optionally checking each member type and applying a member validator.

```python
from datetime import datetime

days = Field().listof(str)
days.value = ["Mo", "Tu", "We"]


def timestamp_validate(value):
    datetime.fromisoformat(value)


timestamps = Field().listof(str, validate=timestamp_validate)
timestamps.value = ["2021-06-15T05:10:33.376787"]
```

For `Model` classes, you can often use `list[Contact]` in the annotation instead.

### `match(regex, flags=0)`

Use `re.match()` against the assigned value.

```python
email = Field(required=True).instance(str).match(r".+@.+")
```

### `search(regex, flags=0)`

Use `re.search()` against the assigned value.

```python
text = Field().instance(str).search(r"dictify")
```

### `model(model_cls)`

Validate nested document data through another `Model`.

```python
from dictify import Field, Model


class Money(Model):
    unit: str = Field(required=True).verify(lambda value: value in ["USD", "GBP"])
    amount: int | float = Field(required=True)


payment = Field().model(Money)
payment.value = {"unit": "USD", "amount": 10.0}
```

For `Model` classes, you can often use `Money` directly in the annotation instead.

### `verify(func, message=None)`

Use a callable that returns `True` or `False`.

```python
age = Field().instance(int).verify(
    lambda value: 0 <= value <= 150,
    "Age range must be 0 to 150",
)
```

### `func(fn)`

Use a callable that raises an exception when the value is invalid.

```python
from datetime import datetime

timestamp = Field().instance(str).func(datetime.fromisoformat)
```

## Standalone Field State

`Field` also stores its own value, so it can be used directly outside of a model.

```python
field = Field(required=True).instance(str)
field.value = "hello"
field.reset()
```

When a `Field` is declared on a `Model` class, that class attribute acts as a shared schema definition. Individual model instances keep their runtime values separately.
