..  dictify documentation master file, created by
    sphinx-quickstart on Tue Apr  7 21:18:31 2020.
    You can adapt this file completely to your liking, but it should at least
    contain the root `toctree` directive.

..  raw:: html

    <img src="./_static/dictify.png" alt="dictify" style="margin-bottom: 1rem;">


Dictify : Documents Schema / Validation made simple
===================================================

.. raw:: html

    <!-- Place this tag in your head or just before your close body tag. -->
    <script async defer src="https://buttons.github.io/buttons.js"></script>
    <!-- Place this tag where you want the button to render. -->
    <!-- Place this tag where you want the button to render. -->
    <a class="github-button" href="https://github.com/nitipit/dictify"
            data-size="large" data-show-count="true"
            aria-label="Star nitipit/dictify on GitHub">
        Star
    </a>

What for ?
**********
**{dictify}** is a python library to define data schema
and validation with simple syntax. It's designed
to use with **documents** data type especially for **JSON** and
**Python Dictionaries**. **{dictify}** use **classes**, **attributes** and
chained methods to make syntax easier to learn and use.

Get it
******

..  code-block:: shell

    pip install dictify

Schema Definition
*****************

For general usage with nested data structure, use ``Model`` and ``Field``
classes to define schemas as example below:

.. code-block:: python

    from dictify import Model, Field

    class User(Model):
        name = Field(required=True).instance(str).match('[a-zA-Z0-9 ._-]+$')  # [1]
        email = Field(required=True).instance(str).match('.+@.+')  # [1]

    class Note(Model):
        title = Field(required=True).instance(str)
        content = Field().instance(str)
        user = Field(required=True).instance(User)

.. epigraph::

    [1] Field validation can be chained.

Data Assignment and Validation
******************************

After schema definition, we can use it by creating ``Model`` instance with
required data.

.. code-block:: python

    user = User({'name': 'user-1', 'email': 'user@example.com'})
    note = Note({'title': 'Title-1', 'user': user})

Furthur data modification will be validated.

.. code-block:: python

    note['title'] = 'Title-2'  # pass validation.
    note['title'] = 0  # Raise Model.Error, require `str` instance.
    note['user']['name'] = 0  # Raise Model.Error, require `str` instance.

.. epigraph::

    **Note :** Use ``try..except`` to catch errors if needed.

Use like Python Dictionaries
****************************
``dictify.Model`` is a subclass of ``dict`` which is validated by
defined schema.

.. code-block:: python

    user.update({'name': 'user-2'})

    note.update({
        'title': 'Title-3',
        'content': 'Content-1',
        'user': user
    })

    # Code below will raise `Model.Error`.
    note.update({'title': 0, 'user': 0})


Convert data to dict() or JSON
******************************

..  code-block:: python

    import json

    note_dict = dict(note)
    note_json = json.dumps(note)

..  epigraph::

    **Note :** For converting to JSON, all data must be instance of ``str``, ``int``,
    ``bool``, ``dict``, ``list``, ``dictify.Model``, ``dictify.ListOf`` or **None** which are **JSON** compatible.


..  toctree::
    :maxdepth: 3
    :hidden:

    model-and-field
    field-api
    validations
    docstring

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
