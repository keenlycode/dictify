<!-- Generated from script, do not edit directly. -->

# Partial Validation

## Standalone Field

Standalone `Field` usage is useful when you want to validate a single value without building the full model.

```python
from dictify import Field

email_field = Field(required=True).instance(str).match(r".+@.+")
email_field.value = "user@example.com"
```

## Reusing Model Fields

You can also reuse a model field definition directly.

```python
from typing import Annotated

from dictify import Field, Model


class User(Model):
    email: Annotated[str, Field(required=True).match(r".+@.+")]


User.email.value = "user@example.com"
```

`User.email` is the shared class-level field definition. When you want an isolated standalone validator, prefer `User.email.clone()`.
