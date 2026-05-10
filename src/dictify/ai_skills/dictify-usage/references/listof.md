<!-- Generated from script, do not edit directly. -->

# ListOf

`Field.listof(...)` stores valid list values as `ListOf`, a list subclass that
keeps validating later item updates.

```python
from dictify import Field

field = Field().listof(str)
field.value = ["one"]
field.value.append("two")
```

## `append(value)`

Append a value after validating it against the `ListOf` item rules.

## `list()`

Return native Python list data, recursively converting nested `Model` and
`ListOf` values.
