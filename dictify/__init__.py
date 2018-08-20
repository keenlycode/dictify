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

        def __call__(self, field):
            return self.func(field, *self.args, **self.kw)

    class Query:
        def __init__(self, value=None):
            self.value  = value
            self.queries = []
            self.errors = []

    def __init__(self):
        """Initialize function for Field()."""
        self.query = Field.Query()
        self.value = None

    def field(func):
        """Decorate function to append verification to `self.queries`."""
        def wrapper(self, *args, **kw):
            verify = Field.Verify(func, *args, **kw)
            self.query.queries.append(verify)
            return self
        return wrapper

    @field
    def required(field):
        """Require value."""
        if (field.value is None) or (field.value == ''):
            raise ValueError('Required')

    @field
    def default(field, default):
        """Set default value."""
        if field.value is None:
            field.value = default

    @field
    def type(field, classinfo):
        """Check value type."""
        if not(isinstance(field.value, classinfo)):
            raise ValueError('Must be %s object' % classinfo)

    @field
    def match(field, re_):
        """Apply re.match to value."""
        if not re.match(re_, field.value):
            raise ValueError("Value not match with '%s'" % re_)

    @field
    def apply(field, func):
        """Apply function to Field(). Receive `self` as first args.

        ## Example use:
        class User(Model):
        def check(self):
            # Do something with self, like checking value or setting value.

        Field().apply(check)
        """
        func(field)


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

    class Field:
        def __init__(self, query):
            self.query = query

        def _verify(self, key, value):
            self.query.value = value
            self.query.errors = list()
            for verify in self.query.queries:
                try:
                    verify(self.query)
                except ValueError as e:
                    self.query.errors.append(e.args[0])
            if self.query.errors:
                raise ValueError("'%s' : %s" % (key, self.query.errors))
            return self.query.value

    def __new__(cls, data=dict()):
        field = dict()
        for k, v in vars(cls).items():
            if isinstance(v, Field):
                field[k] = cls.Field(v.query)
                data[k] = field[k]._verify(k, data.get(k))
        return cls.Dict(data, field)
