**{ dictify }** is a python library to define data schema
and validation with simple syntax. It's designed
to use with **documents** data type especially for **JSON** and
**Python Dictionaries**.

```json
{
    "name": "Dictify Co, Ltd.",
    "contacts": [
        {
            "type": "mail",
            "name": "Ananda, staff",
            "address": "123/321 Sukhumvit Rd. Soi 77 Bangkok, Thailand",
        },
        {
            "type": "phone",
            "name": "",
        },
    ]
}
```

```python
from datetime import datetime
from dictify import Model, Field

class Contact(Model):
    name = Field(required=True)

post = Post({
    'title': 'Dictify',
    'html': 'Hello dictify',
})

print(post)
"""
{
    'title': 'Dictify',
    'timestamp': '2021-06-08T14:53:44.770252',
    'html': 'Hello dictify'
}
"""