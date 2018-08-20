import re
import inspect


class Field:
    """Class contain function to verify Model's fields."""

    class Verify:
        """Class contain verify function to be called later."""

        def __init__(self, func, *args, **kw):
            self.func = func
            self.args = args
            self.kw = kw

        def __call__(self, value):
            return self.func(value, *self.args, **self.kw)

    class Rule:
        """Class to verify rules."""

        def __init__(self):
            self.rules = []
            self.errors = []

        def _verify(self, key, value):
            self.value = value
            self.errors = list()
            for verify in self.rules:
                try:
                    self.value = verify(self.value)
                except ValueError as e:
                    self.errors.append(e.args[0])
            if self.errors:
                raise ValueError("'%s' : %s" % (key, self.errors))
            return self

    def __init__(self):
        self.rule = Field.Rule()
        self.value = None

    def field(func):
        """Decorate function to append function to `self.rule`."""
        def wrapper(self, *args, **kw):
            verify = Field.Verify(func, *args, **kw)
            self.rule.rules.append(verify)
            return self
        return wrapper

    @field
    def required(value):
        """Required."""
        if (value is None) or (value == ''):
            raise ValueError('Required')
        return value

    @field
    def default(value, default: 'default value'):
        """Set default value."""
        if value is None:
            return default
        return value

    @field
    def type(value, classinfo: 'class'):
        """Check value's type."""
        if not(isinstance(value, classinfo)):
            raise ValueError('Must be %s object' % classinfo)
        return value

    @field
    def match(value, re_: 'regular expession string'):
        """Check value matching with regular expression."""
        if not re.match(re_, value):
            raise ValueError("Value not match with '%s'" % re_)
        return value

    @field
    def apply(value, func: 'function to apply'):
        """Apply function to Field().

        ## Example use:
        class User(Model):
            def check(self):
                # Do something with self, like checking value or setting value.

            name = Field().apply(check)
        """
        return func(value)


class Model(dict):
    """Class to defined fields and rules.

    ## Example:
    Class User(Model):
        name = Field().required().type(str)

    user = User({'name': 'John'})
    """

    class Dict(dict):
        """Modified `dict` to strict with field's rules."""

        def __init__(self, data, field):
            self._field = field
            return super().__init__(data)

        def __setitem__(self, k, v):
            self._field[k]._verify(k, v)
            return super().__setitem__(k, v)

    def __new__(cls, field=dict()):
        data = dict()
        for k, v in vars(cls).items():
            if isinstance(v, Field):
                field[k] = v.rule._verify(k, field.get(k))
                data[k] = field[k].value
        return cls.Dict(data, field)
