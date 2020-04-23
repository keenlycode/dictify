Usage
===========

Schema Definition
-----------------

For general usage with nested data structure, use ``Model`` and ``Field``
classes to define schemas as example below:

..  code-block:: python

    from dictify import Model, Field

    class User(Model):
        name = Field(required=True).instance(str).match('^[a-zA-Z ]+$')  # [1]
        email = Field(required=True).instance(str).match('.+@.+')  # [1]

    class Note(Model):
        title = Field(required=True).instance(str)
        content = Field().instance(str)
        user = Field(required=True).instance(User)

..  epigraph::

    [1] Field validation can be chained.

Data Assignment and Validation
------------------------------

After schema definition, we can use it by creating ``Model`` instance with
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
    For converting to JSON, all data must be instance of ``str``, ``int``,
    ``bool``, ``dict``, ``list`` or **None** which are **JSON** compatible.

More about **Field** and **Model**
----------------------------------

**Field** can be defined with validation chain as needed, and can be validated
by ``Field`` itself. For example:

.. code-block:: python

    name = Field(required=True).instance(str).match('^[a-zA-Z ]+$')
    email = Field(required=True).instance(str).match('.+@.+')

    name.value = 'user'
    email.value = 'user@example.com'

    name.value = '0'  # Invalid, value is not assigned.
    email.value = 'user'  # Invalid, value is not assigned.

However, for complex data structure, ``Feild`` can be defined and handle
by ``Model`` which map and validate ``Field`` to python native ``dict``
instance. For example:

.. code-block:: python

    class User(Model):
        name = Field(required=True).instance(str).match('^[a-zA-Z ]+$')
        email = Field(required=True).instance(str).match('.+@.+')

    user = User({'name': 'user', 'email': 'user@example.com'})
    user['name'] = '0' # Invalid, value is not assigned.
    user['email'] = 'user' # Invalid, value is not assigned.
