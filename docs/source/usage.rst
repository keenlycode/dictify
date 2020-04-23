Usage
=====

Schema Definition
-------------------

For general usage with nested data structure, use **Model** and **Field**
classes to define **Schema** as example below:

..  code-block:: python

    from dictify import Model, Field

    class User(Model):
        name = Field(required=True)\
            .instance(str)\
            .verify(lambda field, name: len(name) <= 20)  # [1]

    class Note(Model):
        title = Field(required=True).instance(str)
        content = Field().instance(str)
        user = Field(required=True).instance(User)

..  epigraph::

    [1] Validation can be chained.

Data Assignment and Validation
------------------------------

After schema definition, we can use it by creating **Model** instance with
required data.

..  code-block:: python

    user = User({'name': 'user-1'})
    note = Note({'title': 'Title', 'user': user})

Furthur data modification will be validated.

..  code-block:: python
    
    note['title'] = 'New Title'  # pass validation.
    note['title'] = 0  # Raise Model.Error, require `str` instance.
    note['user']['name'] = 0  # Raise Model.Error, require `str` instance.

Convert data to dict() or JSON
------------------------------

..  code-block:: python

    import json

    note_dict = dict(note)
    note_json = json.dumps(note)

..  epigraph::
    For converting to JSON, all data must be instance of **str**, **int**,
    **boolean**, **dict**, **list** or **None** which are compatible to **JSON**.

Field Validation API
====================

