import re
from functools import wraps

class Field:
    """Class contain function to verify Dictify Field.

    ## Example:
    class User(Model):
        name = Field().required()
    """

    class Verify:
        def __init__(self, func, *args, **kw):
            self.func = func
            self.args = args
            self.kw = kw

        def __call__(self, value):
            return self.func(value, *self.args, **self.kw)

    class Query:
        def __init__(self):
            self.queries = []
            self.errors = []

        def _verify(self, key, value):
            self.value = value
            self.errors = list()
            for verify in self.queries:
                try:
                    self.value = verify(self.value)
                except ValueError as e:
                    self.errors.append(e.args[0])
            if self.errors:
                raise ValueError("'%s' : %s" % (key, self.errors))
            return self.value

    def __init__(self):
        """Initialize function for Field()."""
        self.query = Field.Query()
        self.value = None

    def field(func):
        """Decorate function to append verification to `self.queries`."""
        @wraps(func)
        def wrapper(self, *args, **kw):
            verify = Field.Verify(func, *args, **kw)
            self.query.queries.append(verify)
            return self
        return wrapper

    @field
    def required(value):
        """Require value."""
        if (value is None) or (value == ''):
            raise ValueError('Required')
        return value

    @field
    def default(value, default):
        """Set default value."""
        if value is None:
            return default
        return value

    @field
    def type(value, classinfo):
        """Check value type."""
        if not(isinstance(value, classinfo)):
            raise ValueError('Must be %s object' % classinfo)
        return value

    @field
    def match(value, re_):
        """Apply re.match to value."""
        if not re.match(re_, value):
            raise ValueError("Value not match with '%s'" % re_)
        return value

    @field
    def apply(value, func):
        """Apply function to Field(). Receive `self` as first args.

        ## Example use:
        class User(Model):
        def check(self):
            # Do something with self, like checking value or setting value.

        Field().apply(check)
        """
        return func(value)


class Model(dict):
    class Dict(dict):
        def __init__(self, data, field):
            self._field = field
            return super().__init__(data)

        def __setitem__(self, k, v):
            v = self._field[k]._verify(k, v)
            return super().__setitem__(k, v)

        @property
        def field(self):
            return self._field

    def __new__(cls, data=dict()):
        field = dict()
        for k, v in vars(cls).items():
            if isinstance(v, Field):
                field[k] = v.query
                data[k] = field[k]._verify(k, data.get(k))
        return cls.Dict(data, field)
