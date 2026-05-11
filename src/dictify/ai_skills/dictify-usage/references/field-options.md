<!-- Generated from script, do not edit directly. -->

# Field Options

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

Use `has_default` when you need to know whether a default was configured. `Field(default=None).has_default` is `True`.

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

from dictify import Field, Model


class User(Model):
    email: Annotated[
        str,
        "primary email",
        Field(required=True).match(r".+@.+"),
    ]
    age: Annotated[int | None, Field(default=None)]
```

When `Field(...)` is provided inside `Annotated[...]`, it defines the model field without assigning a class value. Other metadata is ignored for runtime typing.

Direct assignment style remains supported for compatibility:

```python
class User(Model):
    email: str = Field(required=True).match(r".+@.+")
```

This style is fully supported at runtime. For strict static type checking, prefer `Annotated[str, Field(...)]`. Do not combine both forms for the same field.
