Field and Model
===============

``Field`` can be defined with validation chain, and can validated it's value.
For example:

.. code-block:: python

    name = Field(required=True).instance(str).match('[a-zA-Z0-9 ._-]+$')
    email = Field(required=True).instance(str).match('.+@.+')

    name.value = 'user'
    email.value = 'user@example.com'

    name.value = '0'  # Invalid, value is not assigned.
    email.value = 'user'  # Invalid, value is not assigned.

However, using ``Field`` alone doesn't give much benefits. For complex data
structure, ``Feild`` can be defined and managed by ``Model`` which map 
and validate ``Field`` to python native ``dict`` instance. For example:

.. code-block:: python

    class User(Model):
        name = Field(required=True).instance(str).match('[a-zA-Z0-9 ._-]+$')
        email = Field(required=True).instance(str).match('.+@.+')

    user = User({'name': 'user', 'email': 'user@example.com'})
    user['name'] = '0' # Invalid, value won't be assigned.
    user['email'] = 'user' # Invalid, won't be assigned.