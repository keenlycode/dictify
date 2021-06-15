# Validation Recipes

This page contains example of field validation on many type of data which could give enough idea about how to use `dictify.Field`

> For text validation, you can use match() or search() with appropriate Regular Expression patterns.
> - [regexr.com Lean, Build & Test RegEx](https://regexr.com/)
> - [Python RegEX W3Schools](https://www.w3schools.com/python/python_regex.asp)
> - [Google Search: Regular Expression](https://www.google.com/search?q=regular+expression)

## Instance of ...

```python
Field().instance(str)
Field().instance(int)
```

## True / False

```python
Field().instance(bool)
```

## Numbers

Using `instance()` and `verify()` with Python logical and compare operators can verify numbers in many ways.

```python
# 1. number is instance of int or float.
# 2. number is in range [0,10].
Field()\
    .instance((int, float))\
    .verify(lambda value: 0 <= value <= 10)
```

## Subset

Field contains list of days.

```python
Field()\
    .listof(str)\
    .verify(lambda dates:
        set(dates) <= set(['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']))
```

## Choices

```python
Field()\
    .instance(str)\
    .verify(lambda os:
        os in ['android', 'ios'])
```

## Email

```python
Field().match('.+@.+')
```

## Time in ISO format

```python
from datetime import datetime

Field().verify(lambda dt: datetime.fromisoformat(dt))
```

## Images

```python
import io
from PIL import Image

Field()\
    .instance(io.BytesIO)\
    .verify(lambda img:
        Image.open(img).format == 'PNG' or 'JPEG' or 'WEBP' or 'GIF')
```

## UUID (Universally Unique Identifier)

```python
import uuid

Field().instance(uuid.UUID)

# UUID in `str` instance.
Field()\
    .instance(str)\
    .verify(lambda value: uuid.UUID(value))
```