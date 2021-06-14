# Field API

## Field()

Create `Field` object which can validate it's value.

```python
Field(required: bool = False, default: Any = UNDEF, grant: List[Any] = [])
```

### Parameters
---

`required: bool = False`  
Set to **True** if field's value is required.

Required field will raise Field.RequiredError when

1. Get field’s value before assign a valid value.
2. Create Model containing required field but not provide field’s value.
3. Delete required field data form Model instance.

**Example**
```python
email = Field(required=True)
email.value
# Error: `Field.RequiredError`.
# Required value has not been assigned.

email.value = 'user@example.com'
```


`default: Any = UNDEF`  
Default value can be set as static or dynamic (generated) values.

```python
# static value
Field(default=0)

# dynamic or generated value
# make sure to assign function, not it's result.
Field(default=uuid.uuid4)
```

Default value will be set when

1. Create **Field** instance
2. Call `Field().reset()`
3. Create **Model** containing **Field** but doesn’t provide field’s value on creation
4. Delete field’s data from **Model** instance

`grant: List[Any] = []`

```python
Field(grant=[None, ''])
```

Granted Values will always be valid regardless of validators. For example:

```python
field = Field(grant=[None]).instance(str)
field.value = None
```

### Chained methods for validation
---
**Field()** contains methods for validation which can be chained. (Read more at [Model and Field](/guide/model-and-field.html))