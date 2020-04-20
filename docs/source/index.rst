..  dictify documentation master file, created by
    sphinx-quickstart on Tue Apr  7 21:18:31 2020.
    You can adapt this file completely to your liking, but it should at least
    contain the root `toctree` directive.

..  raw:: html

    <img src="./_static/dictify.svg" alt="dictify">

Dictify
=======
    Python ``dict()`` Schema and Validation

Quick Sample
============
..  code-block:: python

    import uuid
    from datetime import datetime
    from dictify import Model, Field

    class User(Model):
        id = Field(default=lambda: uuid.uuid4()).instance(uuid.UUID)
        name = Field(required=True).instance(str)

    class Note(Model):
        title = Field(required=True).instance(str)
        content = Field().instance(str)
        datetime = Field(default=datetime.utcnow()).instance(datetime)
        user = Field(required=True).instance(User)

    user = User({'name': 'user-1'})
    note = Note({'title': 'Title', 'user': user})
    
    note['title'] = 0 # Error

Get it
=======
..  code-block:: python

    pip install dictify


..  toctree::
    :maxdepth: 2
    :hidden:
    
    guide
    api

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
