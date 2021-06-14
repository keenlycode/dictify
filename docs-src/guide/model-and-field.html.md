# Model and Field

`Model` and `Field` are fundamental classes of {dictify}.

`Field` can be defined with validation chain,
and will be validated when value is assigned. For example:

```python
name = Field(required=True).instance(str).match('[a-zA-Z0-9 ._-]+$')
email = Field(required=True).instance(str).match('.+@.+')

name.value = 'user'
email.value = 'user@example.com'

name.value = '0' # Invalid, value is not assigned.
email.value = 'user' # Invalid, value is not assigned.
```

However, using `Field` alone doesn’t give much benefits. For complex data structure, `Feild` can be defined and managed by `Model` which map and validate `Field` to python native `dict` instance. For example:

```python
class User(Model):
    name = Field(required=True).instance(str).match('[a-zA-Z0-9 ._-]+$')
    email = Field(required=True).instance(str).match('.+@.+')

user = User({'name': 'user', 'email': 'user@example.com'})
user['name'] = '0' # Invalid, value won't be assigned.
user['email'] = 'user' # Invalid, won't be assigned.
```

<h1 id="partial-data-validation">Partial data validation</h1>

Defined `Field` can be reused for partial data validation. For example, when user want to update user’s email later, `User.email` can be used as class attributes to validate email without create the whole User object.

```python
email = request.args.get('email')  # pseudo code to get email sent from user.
try:
    User.email.value = email
    # To do : Update user's email to database.
except dictify.FieldError:
    # To do : Report error.
```