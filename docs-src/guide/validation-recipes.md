# Validation Recipes

This page collects small examples for common validation patterns with `dictify.Field`.

For text validation, `match()` and `search()` work well with regular expressions.

## Instance of a Type

```python
Field().instance(str)
Field().instance(int)
```

## Boolean

```python
Field().instance(bool)
```

## Numbers in a Range

```python
Field().instance((int, float)).verify(lambda value: 0 <= value <= 10)
```

## Subset of Allowed Values

```python
Field().listof(str).verify(
    lambda dates: set(dates) <= {"Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"}
)
```

## Choices

```python
Field().instance(str).verify(lambda value: value in ["android", "ios"])
```

## Email

```python
Field().instance(str).match(r".+@.+")
```

## ISO Datetime String

```python
from datetime import datetime

Field().instance(str).func(datetime.fromisoformat)
```

## UUID String

```python
import uuid

Field().instance(str).verify(lambda value: uuid.UUID(value))
```

## Nested Model

```python
from dictify import Field, Model


class Money(Model):
    unit = Field(required=True).verify(lambda value: value in ["USD", "GBP"])
    amount = Field(required=True).instance((int, float))


payment = Field().model(Money)
payment.value = {"unit": "USD", "amount": 10.0}
```

## List of Models

```python
from dictify import Field, Model


class Contact(Model):
    type = Field(required=True).instance(str)
    value = Field(required=True).instance(str)


contacts = Field().listof(Contact)
contacts.value = [
    {"type": "email", "value": "user@example.com"},
    {"type": "phone", "value": "111-800-0000"},
]
```
