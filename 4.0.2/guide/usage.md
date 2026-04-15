# Usage

## Field

`Field` can be used by itself for partial or standalone validation. Values are validated whenever they are assigned.

```python
from dictify import Field

username = Field(required=True).instance(str).match(r"[a-zA-Z0-9 ._-]+$")
email = Field(required=True).instance(str).match(r".+@.+")

username.value = "user"
email.value = "user@example.com"
```

Invalid assignments raise `Field.VerifyError`, and the previous valid values stay unchanged.

## Model

For structured documents, define annotated fields on a `Model` subclass and use `Field(...)` for options or additional validators.

```python
from datetime import UTC, datetime
from typing import Annotated

from dictify import Field, Model


class Contact(Model):
    type: str = Field(required=True).verify(
        lambda value: value in ["phone", "email", "address"]
    )
    note: str = Field().verify(lambda value: len(value) <= 250)
    value: str = Field(required=True).verify(lambda value: len(value) <= 1000)


class User(Model):
    username: str = Field(required=True).match(r"[a-zA-Z0-9 ._-]+$")
    email: Annotated[str, "primary email"] = Field(required=True).match(r".+@.+")
    contacts: list[Contact] = Field()
    created_at: datetime = Field(default=lambda: datetime.now(UTC))
```

## Attribute Access

Declared fields can be accessed as either attributes or mapping keys.

```python
user = User({"username": "user", "email": "user@example.com"})

user.username = "new-user"
user["email"] = "new@example.com"

assert user.username == "new-user"
assert user["email"] == "new@example.com"
```

## Strict Mode

`Model` instances are strict by default.

- `strict=True` rejects undeclared keys and undeclared public attributes
- `strict=False` stores undeclared keys and public attributes as extra model data

```python
user = User({"username": "user", "email": "user@example.com"}, strict=False)

user.nickname = "nick"
user["age"] = 30

assert user.nickname == "nick"
assert user["nickname"] == "nick"
assert dict(user)["age"] == 30
```

With `strict=True`, both `user["age"] = 30` and `user.age = 30` are rejected.

## Annotated

`Annotated[...]` metadata is allowed on model field annotations.

```python
from typing import Annotated


class User(Model):
    email: Annotated[str, "primary email"] = Field(required=True)
```

`dictify` uses `str` as the runtime field type and ignores the extra metadata.

Runtime support for declarations like `email: str = Field(...)` is complete. Static type checker support for that pattern is still limited and may require `cast(Any, Field(...))` depending on the checker.

Do not declare a second `Field(...)` inside `Annotated[...]` when the class attribute is already assigned to `Field(...)`.

```python
# Invalid: ambiguous double-field declaration.
email: Annotated[str, Field(required=True)] = Field()
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

## Partial Data Validation

Standalone `Field` usage is useful when you want to validate a single value without building the full model.

```python
from dictify import Field

email_field = Field(required=True).instance(str).match(r".+@.+")
email_field.value = "user@example.com"
```

You can also reuse a model field definition directly:

```python
from dictify import Field, Model


class User(Model):
    email: str = Field(required=True).match(r".+@.+")


User.email.value = "user@example.com"
```

`User.email` is the shared class-level field definition. When you want an isolated standalone validator, prefer `User.email.clone()`.

## AI Skill

`dictify` also ships a packaged AI skill that can be installed with the built-in CLI:

```shell
dictify ai-skill-install
```

The installer prompts for the destination folder and defaults to `./.agents/skills/dictify-usage`.

See [AI Skill](ai-skill.md).

## Post Validation

Override `post_validate()` when validation depends on multiple fields.

```python
from dictify import Field, Model


class User(Model):
    username: str = Field(required=True).match(r"[a-zA-Z0-9 ._-]+$")
    email: str = Field(required=True).match(r".+@.+")
    email_backup: str = Field(required=True).match(r".+@.+")

    def post_validate(self):
        assert self.get("email") != self.get("email_backup")
```

`post_validate()` runs after successful model creation and after successful mutations such as `__setitem__()`, `update()`, `setdefault()`, and `__delitem__()`.
