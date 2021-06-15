<h1 style="width: 100%; text-align: center; margin-bottom: 0.5rem;">{ Dictify }</h1>

<h2 style="width: 100%; text-align: center; margin-top: 0.5rem;">Documents schema and data validation</h2>

<pkt-tag>{ dictify }</pkt-tag> is a python library to define data schema and validation with simple and flexible syntax for documents data type such as **JSON** and **Python** `dict` object.

## Get it
---

```shell
$ pip install dictify
```

## Schema definition
---
Let's start with an example note data:

```json
{
    'title': 'Dictify',
    'content': 'dictify is easy',
    'timestamp': '2021-06-13T05:13:45.326869'
}
```

The schema condition should be like:

**title**
1. Required field
2. Must be `str` instance
3. Length is <= 300

**content**
1. Must be `str` instance

**timestamp**
1. Required field
2. Default to datetime on creation in ISO format string
3. Must be a valid ISO datetime string


```python
from datetime import datetime
from dictify import Model, Field

class Note(Model):
    title = Field(required=True)\
        .instance(str)\
        .verify(lambda value: len(value) <= 300) # [1]

    content = Field().instance(str)

    timestamp = Field(
            required=True,
            default=lambda: datetime.utcnow().isoformat())\
        .verify(lambda value: datetime.fromisoformat(value))
```

> [1] Field validations can be chained.

## Data assignment and validation
---

After schema definition, now we can use it to create `Model` instance with required data.

```python
note = Note({'title': 'Dictify', 'content': 'dictify is easy'})

# `note` can be used like a dict object.

note.update({
    "content": "Updated content",
})
note["content"] = "Updated again"

# Code below will raise `Model.Error`.
note.update({'title': 0})
note['title'] = 0
```

> Note : Use `try..except` to catch errors if needed.

## Convert data to native 'dict' or 'JSON'
---

```python
import json

note_dict = dict(note) # Convert to python built-in `dict`
note_json = json.dumps(note)  # Convert to JSON string
```