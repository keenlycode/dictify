# Dictify
## Python dict verified :)

`Dictify` is python library to verify dict object.

## Example:
```python
from dictify import *

class User(Model):
    id = Field().type(str)
    name = Field().required().type(str).size(max=100)
    email = Field().required().match('.+@.+')
    gender = Field().any(['m', 'f'])
    age = Field().range([1,150])

```
### Let's see:
```python
>>> user = User()
>>>
```
