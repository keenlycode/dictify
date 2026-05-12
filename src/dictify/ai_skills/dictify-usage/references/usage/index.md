<!-- Generated from script, do not edit directly. -->

# Usage

This page covers the quickest path for using `dictify`. See the deeper usage pages for model behavior, declaration styles, and partial validation patterns.

## Standalone Field

`Field` can validate a single value without defining a model. Values are validated whenever they are assigned.

```python
from dictify import Field

email = Field(required=True).instance(str).match(r".+@.+")
email.value = "user@example.com"
```

Invalid assignments raise `Field.VerifyError`, and the previous valid value stays unchanged.

## Model

For structured documents, define fields on a `Model` subclass. Use `Annotated[..., Field(...)]` when you need defaults, required fields, or extra validators.

```python
from datetime import UTC, datetime
from typing import Annotated

from dictify import Field, Model


class Contact(Model):
    type: Annotated[
        str,
        Field(required=True).verify(
            lambda value: value in ["phone", "email", "address"]
        ),
    ]
    value: Annotated[str, Field(required=True)]


class User(Model):
    username: Annotated[str, Field(required=True).match(r"[a-zA-Z0-9 ._-]+$")]
    email: Annotated[str, Field(required=True).match(r".+@.+")]
    contacts: Annotated[list[Contact], Field()]
    created_at: Annotated[datetime, Field(default=lambda: datetime.now(UTC))]
```

Create validated data from keyword arguments or a mapping, then update it through either attributes or mapping keys.

```python
user = User(
    username="user",
    email="user@example.com",
    contacts=[{"type": "email", "value": "user@example.com"}],
)

same_user = User({"username": "user", "email": "user@example.com"})

user.username = "new-user"
user["email"] = "new@example.com"

assert user.username == "new-user"
assert user["email"] == "new@example.com"
```

## More Usage Topics

- [Model Behavior](model.md)
- [Field Declaration Styles](declaration-styles.md)
- [CLI and AI Agent Inputs](cli-inputs.md)
- [Partial Validation](partial-validation.md)
