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

## Required Fields

Set `required=True` when a value must be present.

Required fields raise `Field.RequiredError` when:

1. You read `field.value` before assigning a valid value.
2. You create a `Model` without providing the required field.
3. You delete a required field from a model.

```python
from dictify import Field

email = Field(required=True)

email.value
email.value = "user@example.com"
```

## Default Values

Defaults can be static values or factories.

```python
import uuid

Field(default=0)
Field(default=uuid.uuid4)
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

## Validation Methods

Field validators can be chained.

```python
username = Field(required=True).instance(str).match(r"[a-zA-Z0-9 ._-]+$")
```

### `instance(type_)`

Verify that the assigned value is an instance of the given type.

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

If `type_` is a `Model` subclass, dict items are validated through that model.

```python
from dictify import Field, Model


class Contact(Model):
    type = Field(required=True).instance(str)
    value = Field(required=True).instance(str)


contacts = Field().listof(Contact)
contacts.value = [{"type": "email", "value": "user@example.com"}]
```

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
    unit = Field(required=True).verify(lambda value: value in ["USD", "GBP"])
    amount = Field(required=True).instance((int, float))


class MoneyTransfer(Model):
    amount = Field(required=True).model(Money)
    fee = Field(required=True).model(Money)


transfer = MoneyTransfer(
    {
        "amount": {"unit": "USD", "amount": 100.0},
        "fee": {"unit": "USD", "amount": 1.0},
    }
)
```

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

`func()` is useful when validation logic needs full Python statements or existing validator functions.

## Standalone Field State

`Field` also stores its own value, so it can be used directly outside of a model.

```python
field = Field(required=True).instance(str)
field.value = "hello"
field.reset()
```

When a `Field` is declared on a `Model` class, that class attribute acts as a shared schema definition. Individual model instances keep their runtime values separately.
