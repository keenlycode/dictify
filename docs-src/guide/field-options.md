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
    email: Annotated[str, "primary email"] = Field(required=True).match(r".+@.+")
    age: int | None = Field(default=None)
```

`Annotated[...]` metadata is ignored for runtime typing unless it contains a `Field(...)`, which is rejected as ambiguous when the class attribute is also assigned to `Field(...)`.
