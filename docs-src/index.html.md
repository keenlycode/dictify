**{ dictify }** is a python library to define data schema
and validation with simple syntax. It's designed
to use with **documents** data type especially for **JSON** and
**Python Dictionaries**.

```json
{
    "name": "Dictify Co, Ltd.",
    "contacts": [
        {
            "type": "address",
            "name": "Office",
            "address": "123/321 Sukhumvit Rd. Soi 77 Bangkok, Thailand",
        },
        {
            "type": "phone",
            "name": "Procurement",
            "number": "+66 81 111 1111
        },
    ]
}
```

```python
from datetime import datetime
from dictify import Model, Field


class Phone(Model):
    type = Field(required=True, default='phone')\
        .verify(lambda value: value == "phone")
    name = Field(required=True).instance(str)
    number = Field(required=True).instance(str)

class Address(Model):
    type = Field(required=True, default='address')\
        .verify(lambda value: value == "address")
    name = Field(required=True).instance(str)
    address = Field(required=True).instance(str)


class Account(Model):
    def contact_validate(value):
        assert isinstance(value, dict)
        if value['type'] == 'phone':
            Phone(value)
        if value['type'] == 'address':
            Address(value)

    name = Field(required=True)
    contacts = Field().listof(validate=contact_validate)


um = Account({
    'name': 'um'
})

phone = Phone({
    'name': 'work',
    'number': '12345678'
})

address = Address({
    'name': 'office',
    'address': 'Some avenue'
})
"""