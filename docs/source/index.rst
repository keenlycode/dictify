..  dictify documentation master file, created by
    sphinx-quickstart on Tue Apr  7 21:18:31 2020.
    You can adapt this file completely to your liking, but it should at least
    contain the root `toctree` directive.

..  raw:: html

    <img src="./_static/dictify.svg" alt="dictify" style="margin-bottom: 1rem;">
    
Dictify : Data schema / validation
==================================
**{dictify}** is a python library to define data schema and validation
with simple syntax. Suitable for handle **Python Dict**, **JSON**
or **Document Oriented** data structure.

Get it
=======
..  code-block:: python

    pip install dictify

Usage Example
=============
Let's say we have to store information about **Note** which contains information
about **User** who wrote it.

Schema
------

..  code-block:: python

    from datetime import datetime
    import json
    from dictify import Model, Field

    class User(Model):
        name = Field(required=True)\
            .instance(str)\
            .verify(lambda field, name: len(name) <= 20)

    class Note(Model):
        title = Field(required=True).instance(str)
        content = Field().instance(str)
        time = Field(default=datetime.utcnow().isoformat())\
            .verify(lambda field, time: datetime.fromisoformat(time))
        user = Field(required=True).instance(User)

    user = User({'name': 'user-1'})
    note = Note({'title': 'Title', 'user': user})
    
    # Now, `note` and `user` are instance of `dict` with schema validation.
    try:
        note['title'] = 0 # Raise Model.Error
    except Model.Error:
        pass

Convert to Dict or JSON
-----------------------

..  code-block:: python

    # continue from the code above.

    note_dict = dict(note)  # Convert to Python's native dict (remove schema).
    note_json = json.dumps(note)  # Convert to json strings.


..  toctree::
    :maxdepth: 2
    :hidden:
    
    docstring

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
