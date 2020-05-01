Validations Recipe
==================

This recipe contains example of field validation on many type of data which
could give enough idea about how to use **Field**

.. epigraph::

    For text validation, you can use ``match()`` or ``search()``
    with appropriate **Regular Expression** patterns.

    - `regexr.com <https://regexr.com/>`_ Lean, Build & Test RegEx
    - `Python RegEX W3Schools <https://www.w3schools.com/python/python_regex.asp>`_
    - `Google Search: Regular Expression <https://www.google.com/search?q=regular+expression>`_


Instance of ...
***************

.. code-block:: python

    Field().instance(str)
    Field().instance(int)

True/False
**********

.. code-block:: python

    Field().instance(bool)

Numbers
*******

Using  ``instance()`` and ``verify()`` with Python **logical** and **compare**
operators can verify numbers in many ways.

.. code-block:: python

    # 1. number is instance of int or float.
    # 2. number is in range [0,10].
    Field()\
        .instance((int, float))\
        .verify(lambda value: 0 <= value <= 10)

Subset
******

This example define **Field** contains list of days.

.. code-block:: python

    Field()\
        .listof(str)\
        .verify(lambda dates:
            set(dates) <= set(['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']))

Choices
*******

.. code-block:: python

    Field()\
        .instance(str)\
        .verify(lambda os:
            os in ['android', 'ios'])

Email
*****

.. code-block:: python

    Field().match('.+@.+')

DateTime in ISO Format
**********************

.. code-block:: python

    from datetime import datetime

    Field().verify(lambda dt: datetime.fromisoformat(dt))

Images
******

.. code-block:: python

    import io
    from PIL import Image

    Field()\
        .instance(io.BytesIO)\
        .verify(lambda img:
            Image.open(img).format == 'PNG' or 'JPEG' or 'WEBP' or 'GIF')

UUID
****

`Universally Unique Identifier <https://www.google.com/search?q=Universally%20Unique%20Identifier>`_

.. code-block:: python

    import uuid

    Field().instance(uuid.UUID)

    # UUID in `str` instance.
    Field()\
        .instance(str)\
        .verify(lambda value: uuid.UUID(value))
