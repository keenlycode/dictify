# Usage

<h2 id="field">Field</h2>

---

**Field** can be defined with validation chain,
and will be validated when value is assigned. For example:

```python
from dictify import Field

username = Field(required=True).instance(str).match('[a-zA-Z0-9 ._-]+$')
email = Field(required=True).instance(str).match('.+@.+')

username.value = 'user'
email.value = 'user@example.com'

username.value = 0 # Invalid, value is not assigned.
email.value = 'user' # Invalid, value is not assigned.
```

<h2 id="model">Model</h2>

---

For complex or nested data structure, **Feild** can be defined and managed by **Model** which map and validate **Field** to python native **dict** instance. For example:

```python
from dictify import Field, Model

class User(Model):
    username = Field(required=True).instance(str).match('[a-zA-Z0-9 ._-]+$')
    email = Field(required=True).instance(str).match('.+@.+')

user = User({'username': 'user', 'email': 'user@example.com'})
user['username'] = 0 # Invalid, value won't be assigned.
user['email'] = 'user' # Invalid, won't be assigned.
user['age'] = 30 # Error, undefined field.
```

<h3 id="strict-mode"># Strict mode</h3>

By default, **Model** object will be created in **strict mode** which won't allow value assignment on undefined field. Set `strict=False` at Model creation to change this behavior.

```python
user = User({'username': 'user', 'email': 'user@example.com'}, strict=False)

# Value assignment on undefined field is allowed.
user['age'] = 30
```

<h2 id="partial-data-validation">Partial data validation</h2>

---

Defined `Field` can be reused for partial data validation. For example, when user want to update user’s email later, `User.email` can be used as class attributes to validate email without create the whole User object.

```python
email = request.args.get('email')  # pseudo code to get email sent from user.
try:
    User.email.value = email
    # To do : Update user's email to database.
except dictify.FieldError:
    # To do : Report error.
```

<h2 id="post-validation">Post validation</h2>

---

Define `post_validation()` method and it will be applied everytime data is set.

```python
class User(Model):
    username = Field(required=True).instance(str).match('[a-zA-Z0-9 ._-]+$')
    email = Field(required=True).instance(str).match('.+@.+')
    email_backup = Field(require=True).instance(str).match('.+@.+')

    def post_validation(self):
        # Email duplication check, all built-in dictionary methods can be used.
        assert self.get('email') != self.get('email_backup')
```