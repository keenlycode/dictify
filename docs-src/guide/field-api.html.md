# dictify.Field API

## Field()
---

`dictify.Field()` creates **Field** object which can validate it's value.

```python
Field(
    required: bool = False, # Required field
    default: Any = UNDEF, # Default value
    grant: List[Any] = [] # Granted values
)
```

### \# Required field

Set `required=True` if value is required.

Required field will raise Field.RequiredError when

1. Get field’s value before assign a valid value.
2. Create Model containing required field but not provide field’s value.
3. Delete required field data form Model instance.

```python
email = Field(required=True)
email.value
# Error: `Field.RequiredError`.
# Required value has not been assigned.

email.value = 'user@example.com'
```

### \# Default value

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

### \# Granted values

Granted values will always be valid regardless of validators. For example:

```python
field = Field(grant=[None]).instance(str)
field.value = None # valid
```

## Validation methods
---

**Field()** contains methods for validation which can be chained. (Read more at [Model and Field](/guide/model-and-field.html))


### <pkt-tag>def</pkt-tag> Instance(type_)
<div class="code-label">param</div>

```python
type_: 'type or Tuple[type, ...]'
```

Verify that assigned value is an instance of specified `type`.

```python
email = Field().instance(str)
email.value = 'user@example.com'

number = Field().instance((int, float))
number.value = 0 # valid
number.value = 0.1 # valid
number.value = 1 + 2j # invalid
```

### <pkt-tag>def</pkt-tag> listof(type_, validate=None)
<div class="code-label">param</div>

```python
type_ : 'type or Tuple[type, ...]'
validate: Callable[value] = None
```

Verify that assigned value is a list of specified `type`.

```python
from datetime import datetime

dates = Field().listof(str)
dates.value = ['Mo', 'Tu', 'We']
dates.value = [0, 1, 2]  # Field.VerifyError

def timestamp_validate(value):
    datetime.fromisoformat(value)

timestamp = Field().listof(validate=timestamp_validate)
timestamp.value = ['2021-06-15T05:10:33.376787'] # valid
timestamp.value.append(1) # invalid
```

### <pkt-tag>def</pkt-tag> match(regex)
### <pkt-tag>def</pkt-tag> search(regex)
<div class="code-label">param</div>

```python
regex: 'Regular expression'
```

Match value with regular expression pattern.  
There're 2 methods to use either `re.match` or `re.search`

```python
email = Field(required=True).instance(str).match('.+@.+')
email.value = 'user@example.com'
email.value = 0  # Field.VerifyError
```

### <pkt-tag>def</pkt-tag> model(model_cls)
<div class="code-label">param</div>

```python
model_cls: dictify.Model
```
Verify that value pass given **Model** validation.  
Very useful for nested data structure.

```python
from dictify import Model, Field
from datetime import datetime
import uuid

def verify_uuid1(value):
    assert isinstance(value, str)
    id_ = uuid.UUID(value)
    assert id_.version == 1

class Money(Model):
    unit = Field(required=True)\
        .verify(lambda value: value in ['USD', 'GBP'])
    amount = Field(required=True).instance((int,float))

class MoneyTransfer(Model):
    sender = Field(required=True).func(verify_uuid1)
    receiver = Field(required=True).func(verify_uuid1)
    amount = Field(required=True).model(Money) # [*]
    fee = Field(required=True).model(Money) # [*]
    timestamp = Field(required=True)\
        .verify(lambda value: datetime.fromisoformat(value))

transfer = MoneyTransfer({
    "sender": "4782af1a-cdac-11eb-bfc9-04d3b02081c2",
    "receiver": "156cd9d2-cdad-11eb-bfc9-04d3b02081c2",
    "amount": {
        "unit": "USD",
        "amount": 100.00
    },
    "fee": {
        "unit": "USD",
        "amount": 1.00
    },
    "timestamp": "2021-06-15T07:44:25.209164"
})
```

### <pkt-tag>def</pkt-tag> verify(lambda_, message)
<div class="code-label">param</div>

```python
lambda_: def(value) -> bool
message: str
```

Designed to use with `lambda` for simple syntax since ``lambda``
can't use ``assert`` statement.  
The callable must return `bool` instance.  
If return ``False``, It will be raised as ``AssertionError``.

```python
age = Field().instance(int).verify(
    lambda value: 0 <= value <= 150,
    "Age range must be 0 - 150"
)
```

### <pkt-tag>def</pkt-tag> func(callable_)
<div class="code-label">param</div>

```python
callable_: def(value) -> None
```

Apply function to verify value and raise Exception if value is invalid.


```python
# callable function to verify uuid4 value
def is_uuid4(value):
    assert isinstance(value, str), "Value must be instance of `str`"
    id = uuid.UUID(value)
    # Raise AssertionError if id.version != 4
    assert id.version == 4, "Value must be UUID version 4 format"

uuid4 = Field().func(is_uuid4)

uuid4.value = str(uuid.uuid4())
uuid4.value = 1  # invalid, raise Exception
```

`func()` provide more control to verify value since it can use statements and raise `Exception`

> Understanding try..except and assert will leverage usage benefits.
> See links below to learn more about Python assert statement.
> - [https://www.w3schools.com/python/ref_keyword_assert.asp](https://www.w3schools.com/python/ref_keyword_assert.asp)
> - [https://www.google.com/search?q=python+assert&oq=python+assert](https://www.google.com/search?q=python+assert&oq=python+assert)