<!-- Generated from script, do not edit directly. -->

# Field Declaration Styles

## Annotated Style

`Annotated[...]` metadata can declare a model field without assigning a class value.

```python
from typing import Annotated

from dictify import Field, Model


class User(Model):
    email: Annotated[str, Field(required=True).match(r".+@.+")]
```

`dictify` uses `str` as the runtime field type and uses `Field(...)` as the field definition. This style is friendly to static type checkers because the model attribute is annotated as `str` without assigning a `Field` object to it.

Additional `Annotated[...]` metadata is allowed and ignored for runtime typing.

```python
class User(Model):
    email: Annotated[str, "primary email", Field(required=True)]
```

## Direct Assignment Style

`dictify` also supports assigning `Field(...)` directly to the class attribute:

```python
class User(Model):
    email: str = Field(required=True).match(r".+@.+")
```

This style is fully supported at runtime and can be concise for scripts or existing code. For strict static type checking, prefer `Annotated[str, Field(...)]`.

## Invalid Mixed Style

Do not declare a second `Field(...)` inside `Annotated[...]` when the class attribute is already assigned to `Field(...)`.

```python
# Invalid: ambiguous double-field declaration.
email: Annotated[str, Field(required=True)] = Field()
```
