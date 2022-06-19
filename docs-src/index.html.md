<h1 style="width: 100%; text-align: center; margin-bottom: 0.5rem;">{ Dictify }</h1>

<h2 style="width: 100%; text-align: center; margin-top: 0.5rem;">Schema and data validation for Python</h2>

<div style="display: flex; justify-content: center;">
    <a class="button"
            href="https://github.com/nitipit/dictify">
        <el-icon set="brand" name="github" style="margin-right: 0.2rem;"></el-icon>
        Github
    </a>
</div>

<pkt-tag>{ dictify }</pkt-tag> is a python library to define data schema and validation with simple and flexible syntax for documents data type such as **JSON** and **Python** `dict` object.

<div id="new-features">
    <div class="row">
        <pkt-badge style="padding:0.1rem 0.5rem;">! New in V3.2.0</pkt-badge>
        <code>Model.dict()</code> Return data as native dict and list
    </div>
    <div class="row" style="margin-top: 0.5rem;">
        <pkt-badge style="padding:0.1rem 0.5rem;">! New in V3.1.0</pkt-badge>
        <a href="guide/usage.html#strict-mode" class="pkt-box-arrow-left">strict mode</a>
        <a href="guide/usage.html#post-validation" class="pkt-box-arrow-left">post validation</a>
    </div>
</div>

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
    "title": "Dictify",
    "content": "dictify is easy",
    "timestamp": "2021-06-13T05:13:45.326869"
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

## Create data instance with defined schema.
---

```python
note = Note({'title': 'Dictify', 'content': 'dictify is easy'})
```

### Use it like dict instance with schema ;)

Worry free, invalid data can't be assigned at anytime.


```python
# `note` can be used like a dict object.
note.update({"content": "Updated content"})
note["content"] = "Updated again"

# Code below will raise `Model.Error`.
note.update({'title': 0})
note['title'] = 0
```

> Note : Use `try..except` to catch errors if needed.


## Convert data to native `dict` or `JSON`
---

```python
import json

note_dict = dict(note) # Convert to python built-in `dict`
note_json = json.dumps(note)  # Convert to JSON string
```