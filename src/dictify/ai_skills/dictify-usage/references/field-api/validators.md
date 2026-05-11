<!-- Generated from script, do not edit directly. -->

# Field Validators

Field validators can be chained.

```python
from dictify import Field

username = Field(required=True).instance(str).match(r"[a-zA-Z0-9 ._-]+$")
```

## `instance(type_)`

Verify that the assigned value is an instance of the given type.

For `Model` fields, prefer annotations for the base type. `instance(...)` remains useful for standalone `Field` validation and compatibility.

```python
email = Field().instance(str)
email.value = "user@example.com"

number = Field().instance((int, float))
number.value = 0
number.value = 0.1
```

## `listof(type_=UNDEF, validate=None)`

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

## `match(regex, flags=0)`

Use `re.match()` against the assigned value.

```python
email = Field(required=True).instance(str).match(r".+@.+")
```

## `search(regex, flags=0)`

Use `re.search()` against the assigned value.

```python
text = Field().instance(str).search(r"dictify")
```

## `model(model_cls)`

Validate nested document data through another `Model`.

```python
from typing import Annotated

from dictify import Field, Model


class Money(Model):
    unit: Annotated[
        str,
        Field(required=True).verify(lambda value: value in ["USD", "GBP"]),
    ]
    amount: Annotated[int | float, Field(required=True)]


payment = Field().model(Money)
payment.value = {"unit": "USD", "amount": 10.0}
```

For `Model` classes, you can often use `Money` directly in the annotation instead.

## `verify(func, message=None)`

Use a predicate-style callable for validation.

The callable may raise its own exception or return a truthy value. Falsy
return values fail validation and surface as `Field.VerifyError`.

```python
age = Field().instance(int).verify(
    lambda value: 0 <= value <= 150,
    "Age range must be 0 to 150",
)
```

## `func(fn)`

Use a callable to transform or validate the value.

If the callable returns a value, that value becomes the field value. If it
raises an exception, validation fails and surfaces as `Field.VerifyError`.

```python
from datetime import datetime

timestamp = Field().instance(str).func(datetime.fromisoformat)
```
