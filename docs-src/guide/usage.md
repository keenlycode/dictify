# Usage

## Field

`Field` can be used by itself for partial or standalone validation. Values are validated whenever they are assigned.

```python
from dictify import Field

username = Field(required=True).instance(str).match(r"[a-zA-Z0-9 ._-]+$")
email = Field(required=True).instance(str).match(r".+@.+")

username.value = "user"
email.value = "user@example.com"

username.value = 0
email.value = "user"
```

The last two assignments raise `Field.VerifyError`, and the previous valid values stay unchanged.

## Model

For structured documents, define `Field` instances on a `Model` subclass.

```python
from dictify import Field, Model


class Contact(Model):
    type = Field(required=True).instance(str).verify(
        lambda value: value in ["phone", "email", "address"]
    )
    note = Field().instance(str).verify(lambda value: len(value) <= 250)
    value = Field(required=True).instance(str).verify(
        lambda value: len(value) <= 1000
    )


class User(Model):
    username = Field(required=True).instance(str).match(r"[a-zA-Z0-9 ._-]+$")
    email = Field(required=True).instance(str).match(r".+@.+")
    contacts = Field().listof(Contact)


user = User({"username": "user", "email": "user@example.com"})
user["username"] = "new-user"

# These raise Model.Error.
user["username"] = 0
user["email"] = "user"
user["age"] = 30
```

## Strict Mode

`Model` instances are strict by default. In strict mode, assigning to an undeclared key raises `Model.Error`.

```python
user = User({"username": "user", "email": "user@example.com"}, strict=False)

user["age"] = 30
```

With `strict=False`, extra keys are allowed and stored as plain mapping data.

## Native Data

Use `dict(model)` or `model.dict()` when you need plain Python data.

- `dict(model)` returns a shallow `dict`
- `model.dict()` recursively converts nested `Model` and `ListOf` values

```python
import json

user = User(
    {
        "username": "user",
        "email": "user@example.com",
        "contacts": [
            {"type": "phone", "value": "111-800-0000"},
        ],
    }
)

payload = user.dict()
message = json.dumps(user.dict())
```

## Partial Data Validation

Standalone `Field` usage is useful when you want to validate a single value without building the full model.

```python
from dictify import Field

email_field = Field(required=True).instance(str).match(r".+@.+")

email_field.value = "user@example.com"
```

You can also reuse a model field definition directly:

```python
from dictify import Field


class User(Model):
    email = Field(required=True).instance(str).match(r".+@.+")


User.email.value = "user@example.com"
```

This pattern is useful for validating patch-style updates before writing them elsewhere.

## Post Validation

Override `post_validate()` when validation depends on multiple fields.

```python
from dictify import Field, Model


class User(Model):
    username = Field(required=True).instance(str).match(r"[a-zA-Z0-9 ._-]+$")
    email = Field(required=True).instance(str).match(r".+@.+")
    email_backup = Field(required=True).instance(str).match(r".+@.+")

    def post_validate(self):
        assert self.get("email") != self.get("email_backup")
```

`post_validate()` runs after successful model creation and after successful mutations such as `__setitem__()`, `update()`, `setdefault()`, and `__delitem__()`.
