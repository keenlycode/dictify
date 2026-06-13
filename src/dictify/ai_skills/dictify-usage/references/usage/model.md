<!-- Generated from script, do not edit directly. -->

# Model Behavior

## Attribute and Mapping Access

Declared fields can be accessed as either attributes or mapping keys.

```python
from typing import Annotated

from dictify import Field, Model


class User(Model):
    username: Annotated[str, Field(required=True)]
    email: Annotated[str, Field(required=True).match(r".+@.+")]


user = User(username="user", email="user@example.com")

user.username = "new-user"
user["email"] = "new@example.com"

assert user.username == "new-user"
assert user["email"] == "new@example.com"
```

## Native Data

Use `dict(model)` or `model.dict()` when you need plain Python data.

- `dict(model)` returns a shallow `dict`
- `model.dict()` recursively converts nested `Model` and `ListOf` values

```python
import json

payload = user.dict()
message = json.dumps(user.dict())
```

## Strict Mode

`Model` instances are strict by default.

- `_strict=True` rejects undeclared keys and undeclared public attributes
- `_strict=False` stores undeclared keys and public attributes as extra model data

```python
user = User(username="user", email="user@example.com", _strict=False)

user.nickname = "nick"
user["age"] = 30

assert user.nickname == "nick"
assert user["nickname"] == "nick"
assert dict(user)["age"] == 30
```

With `_strict=True`, both `user["age"] = 30` and `user.age = 30` are rejected.

Mapping input remains useful for JSON-like data, while keyword input fits Python object construction:

```python
User({"username": "user", "email": "user@example.com"})
User(username="user", email="user@example.com")
```

`Model` subclasses also expose an inspectable keyword constructor signature for tools that use `inspect.signature()`, including CLI libraries such as Cyclopts. See [CLI and AI Agent Inputs](cli-inputs.md) for a full example.

```python
import inspect

assert str(inspect.signature(User)) == "(*, username: str, email: str)"
```

The advanced `_strict` constructor keyword remains accepted at runtime, but it is intentionally hidden from generated public signatures so signature-driven tools expose declared model fields only.

## Post Validation

Override `post_validate()` when validation depends on multiple fields.

```python
from typing import Annotated

from dictify import Field, Model


class User(Model):
    username: Annotated[str, Field(required=True).match(r"[a-zA-Z0-9 ._-]+$")]
    email: Annotated[str, Field(required=True).match(r".+@.+")]
    email_backup: Annotated[str, Field(required=True).match(r".+@.+")]

    def post_validate(self):
        assert self.get("email") != self.get("email_backup")
```

`post_validate()` runs after successful model creation and after successful mutations such as `__setitem__()`, `update()`, `setdefault()`, and `__delitem__()`.
