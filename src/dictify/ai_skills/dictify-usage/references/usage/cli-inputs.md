<!-- Generated from script, do not edit directly. -->

# CLI and AI Agent Inputs

Dictify models can describe validated command inputs for human users, scripts, and AI agents.

`Model` subclasses expose an inspectable keyword constructor signature, so tools that use `inspect.signature()` can discover model fields. This makes Dictify models work well with CLI libraries such as Cyclopts.

## Why this matters

Modern AI agents often call tools through CLI commands. A Dictify model lets you keep one schema for:

- validated Python construction
- JSON-like mapping validation
- CLI argument binding
- AI-agent tool input validation

```python
from typing import Annotated

from dictify import Field, Model


class CreateUser(Model):
    name: Annotated[str, Field(required=True)]
    email: Annotated[str, Field(required=True).match(r".+@.+")]
```

The same model accepts Python keyword input and mapping input:

```python
CreateUser(name="Ada", email="ada@example.com")
CreateUser({"name": "Ada", "email": "ada@example.com"})
```

## Inspectable signatures

Tools can inspect a model class and discover its fields.

```python
import inspect

assert str(inspect.signature(CreateUser)) == "(*, name: str, email: str)"
```

Required fields appear without defaults. Fields with `Field(default=...)` expose that default in the signature. `_strict` remains the Dictify constructor option for controlling unknown keys and attributes, but it is hidden from generated public signatures so signature-driven tools expose declared model fields only.

## Cyclopts example

Use a Dictify model as a structured CLI parameter.

```python
from typing import Annotated

from cyclopts import App
from dictify import Field, Model


class CreateUser(Model):
    name: Annotated[str, Field(required=True)]
    email: Annotated[str, Field(required=True).match(r".+@.+")]


app = App()


@app.default
def main(user: CreateUser):
    print(user.name)
    print(user.email)


app()
```

Run it with nested options:

```shell
python app.py --user.name Ada --user.email ada@example.com
```

Cyclopts constructs `CreateUser(name="Ada", email="ada@example.com")`, and Dictify validates assignments through the model fields.
