Field API
=========

Field()
*******

.. code-block:: python

    Field(required=False, default=UNDEF, disallow=[])

# Required Field
----------------

.. code-block:: python

    Field(required=True)

Required field will raise ``Field.RequiredError`` when

1. Get field's value before assign valid value.
2. Create **Model** containing required field but not provide field's value.
3. Delete required field data form **Model** instance.

# Default Value
---------------

Default value can be set as static or dynamic (generated) value.

.. code-block:: python

    # static value
    Field(default=0)

    # dynamic or generated value
    # make sure you assign function, not it's result.
    Field(default=uuid.uuid4)

Default value will be set when

1. Create **Field** instance
2. Call ``Field().reset()``
3. Create **Model** containing **Field** but doesn't provide field's value
   on creation
4. Delete field's data from ``Model`` instance

# Disallowed Value
------------------

.. code-block:: python

    Field(disallow=[None, ''])

**Field** will raise ``Field.VerifyError`` when assign disallowed value.

instance(type)
**************
Verify that assigned value is an instance of ``type``

.. code-block:: python
    
    email = Field().instance(str)
    email.value = 'user@example.com'

listof(type)
************
Verify that assigned value is a list of ``type``

.. code-block:: python

    dates = Field().listof(str)
    dates.value = ['Mo', 'Tu', 'We']
    dates.value = [0, 1, 2]  # Field.VerifyError

match(pattern) / search(pattern)
********************************
Match value with regular expression pattern.

.. code-block:: python

    email = Field(required=True).instance(str).match('.+@.+')
    email.value = 'user@example.com'
    email.value = 0  # Field.VerifyError

model(Model)
************
Verify that value pass given **Model** validation. (used in code line: 8)

.. code-block:: python
    :linenos:

    class User(Model):
        name = Field(required=True).instance(str).match('[a-zA-Z0-9 ._-]+$')
        email = Field(required=True).instance(str).match('.+@.+')

    class Note(Model):
        title = Field(required=True).instance(str)
        content = Field().instance(str)
        user = Field(required=True).model(User)

    user = {'name': 'user-1', 'email': 'user@example.com'}
    note = Note({'title': 'Title-1', 'user': user})

We can notice that we might use ``Field.instance()`` in this case. However,
Using ``Field.model()`` is easier to validate complex **dict** or **JSON** data.
    

verify(lambda, message)
***********************
Verify value using ``lambda``

.. code-block:: python

    age = Field().instance(int).verify(
        lambda value: 0 <= value <= 150,
        "Age range must be 0 - 150"
    )

func(callable)
**************
Use ``callable`` function with **value** as an argument.

``callable`` should return ``Exception`` if **value** is invalid.

.. code-block:: python

    import uuid
    from dictify import Field

    # callable function to verify uuid4 value
    def is_uuid4(value):
        assert isinstance(value, str), "Value must be instance of `str`"
        id = uuid.UUID(value)
        # Raise AssertionError if id.version != 4
        assert id.version == 4, "Value must be UUID version 4 format"

    uuid4 = Field().func(is_uuid4)

    uuid4.value = str(uuid.uuid4())
    uuid4.value = 1  # invalid, raise Exception

``func()`` provide more control to verify value since it can use statements
and raise ``Exception``

.. epigraph::

    Understanding ``try..except`` and ``assert`` will leverage usage benefits.

    See links here to learn more about Python ``assert`` statement.

    - https://www.w3schools.com/python/ref_keyword_assert.asp
    - https://www.google.com/search?q=python+assert&oq=python+assert