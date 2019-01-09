<img src="https://nitipit.github.io/dictify/static/asset/dictify.svg">

## Python `dict` and `json` verification for humankind :)

`dictify` is python library to verify `dict` object and `json` with easy syntax and chainable rules.

## Install
```bash
pip install dictify
```

## Example:
```python
from dictify import *
import uuid

class User(Model):
    id = Field().default(uuid.uuid4()).type(uuid.UUID)
    name = Field().required().type(str).length(max=100)
    email = Field().required().match('.+@.+')
    gender = Field().anyof(['m', 'f'])
    age = Field().number(min=0, max=150)
```

## Features
### Auto verify new dict object.
```python
>>> user = User()
ValueError: {'name': ['Required.'], 'email': ['Required.']}

>>> user = User({
...     'name': 'test-user',
...     'email': 'user@example.com'
... })

>>> user
{'id': UUID('11fadebb-3c70-47a9-a3f0-ebf2a3815993'),
 'name': 'test-user',
 'email': 'user@example.com',
 'gender': None,
 'age': None}
```

### Verify dict object on the fly.
```python
>>> user['age'] = 200 # user['age'] rule is number(min=0, max=150)
ValueError: ['Value is 200, must be 0 to 150']
>>> user['age'] = 20
>>> user['gender'] = 'm'
{'name': 'test-user',
 'email': 'user@example.com',
 'id': UUID('b3acc59d-93cc-4f58-92d6-a3340b7a6678'),
 'gender': 'm',
 'age': 20}
```

### Chainable rules.
As you can see in `User(Model)` in example above, fields' rules is chainable.
```python
name = Field().required().type(str).length(max=100)
# `name` value required string type with max length = 100
```

## To use with `json`
use `json` package to transform between `json` and `dict`
```python
from dictify import *
import json

class User(Model):
    name = Field().required().type(str).length(max=100)
    email = Field().required().type(str).length(max=100)

user = json.loads('{"name": "test-user", "email": "user@example.com"}')
user = User(user)
```

## Rules
- `anyof(members: list)`: Value must be any of defined `members`
- `apply(func: function)`: Apply function to value. The applied function will get field's value as it's first argument. For example:
    ```python
    from dictify import Model, Field
    import uuid
    from unittest import TestCase

    test_case = TestCase()

    class User(Model):
        def uuid4_rule(value):
            id_ = uuid.UUID(value)
            test_case.assertEqual(id_.version, 4)

        id_ = Field().apply(uuid4_rule)
    ```
- `default(default_: Any)`: Set default value.
- `length(min: int, max: int)`: min/max constrain to value's length using `len()`.
- `listof(type_: type)`: A list which contain object type as specified. For example:
   ```python
   comments = Field().listof(str)
   ```
- `match(re_: 'regex pattern')`: Check value match with regex pattern.
- `number(min: 'number', max: 'number')`: Define min/max number constrain to value.
- `required()`: Value is required (Not `None` or `''`).
- `subset(members: list)`: Value must be subset of defined `members`
- `type(type_: type`): Define value's type.
