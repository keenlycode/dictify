Field Validation API
====================

Field(required=False, disallow=[], default=UNDEF)
*************************************************
Init ``Field`` instance with options:

.. raw:: html

    <style>
    table[el="field"] td.center {
        text-align: center;
    }
    table[el="field"] code {
        color: blue;
        vertical-align: middle;
    }
    </style>

    <table el="field" class="bits-ui" style="margin-bottom: 2rem;">
        <thead>
            <tr><th>Option</th><th>Type</th><th>Default</th><th>Description</th>
        </thead>
        <tbody>
            <tr>
                <td class="center">required</td>
                <td class="center">bool</td>
                <td class="center">False</td>
                <td>
                    If set to <code>True</code>, getting value from the field
                    without value assinged will raise <code>Field.RequiredError</code>
                </td>
            </tr>
            <tr>
                <td class="center">disallow</td>
                <td class="center">list</td>
                <td class="center">[]</td>
                <td>
                    List of disallow value. Raise <code>Field.VerifyError</code>
                    if disallowed value is assinged.
                </td>
            </tr>
            <tr>
                <td class="center">default</td>
                <td class="center">Any</td>
                <td class="center">UNDEF</td>
                <td>
                    Default value when creating Field or call
                    <code>Field.reset()</code>
                </td>
            </tr>
        </tbody>
    </table>

**Example :**

.. code-block:: python

    email = Field(required=True, disallow=[None, ''])
    value = email.value  # Field.RequiredError, since value has not assigned.
    email.value = None  # Field.VerifyError, assigned value is disallowed.

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
Verify that value pass given **Model** validation. (defined in code line: 8)

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
Using ``Field.model()`` is easier to validate complex **JSON** data since it can
accept native ``dict`` instance for the whole tree.
    

verify(lambda, message)
***********************
Verify value using lambda

.. code-block:: python

    age = Field().instance(int).verify(lambda value: 0 <= value <= 150)

func(callable)
**************
