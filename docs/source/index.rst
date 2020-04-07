..  dictify documentation master file, created by
   sphinx-quickstart on Tue Apr  7 21:18:31 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

..  raw:: html

    <img src="./_static/dictify.svg" alt="dictify">
    <h2><code>dict()</code> schema and validation just like eating banana.</h2>

Example
=======
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
    
    # print(note)
    # {
    #     'datetime': datetime.datetime(2020, 4, 7, 15, 5, 4, 800777),
    #     'title': 'Title',
    #     'user': {
    #         'id': UUID('5d4ad959-ac18-4e47-99ef-13b3e6797d17'),
    #         'name': 'user-1'
    #     }
    # }

..  toctree::
    :maxdepth: 2
    :hidden:

    guide
    reference

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
