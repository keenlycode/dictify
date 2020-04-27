Validations Recipe
==================

Instance of ...
***************

Verify value instance or type.

.. code-block:: python

    Field().instance(str)
    Field().instance(int)
    Field().instance(bool)

Numbers
*******

``instance()`` and ``verify()`` can be chained to verify numbers in many ways.

.. code-block:: python

    # 1. number is instance of int or float.
    # 2. number is in range [0,10].
    Field().instance((int, float))\
        .verify(lambda value: 0 <= value <= 10,
            'Number must be in range [0,10]')