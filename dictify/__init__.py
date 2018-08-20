import re
from functools import wraps

class Field:
    """Class contain function to verify Dictify Field.

    ## Example:
    class User(Model):
        name = Field().required()
    """

    class Func:
        def __init__(self, field, func, *args, **kw):
            self.func = func
            self.args = args
            self.kw = kw

        def __call__(self, field):
            return self.func(field, *self.args, **self.kw)

    class Verify:
        def __init__(self):
            self.verifies = []
            self.errors = []

    def __init__(self):
        """Initialize function for Field()."""
        self.verify = Field.Verify()
        self.value = None

    def field(func):
        """Decorate function to append verification to `self.queries`."""
        def wrapper(self, *args, **kw):
            f = Field.Func(self, func, *args, **kw)
            self.verify.verifies.append(f)
            return self
        return wrapper

    def _verify(self, key, value):
        self.value = value
        self.verify.errors = list()
        for v in self.verify.verifies:
            try:
                v(self)
            except ValueError as e:
                self.verify.errors.append(e.args[0])
        if self.verify.errors:
            raise ValueError("'%s' : %s" % (key, self.verify.errors))
        return self.value

    @field
    def required(self):
        """Require value."""
        if (self.value is None) or (self.value == ''):
            raise ValueError('Required')

    @field
    def default(self, default):
        """Set default value."""
        if self.value is None:
            self.value = default

    @field
    def type(self, classinfo):
        """Check value type."""
        if not(isinstance(self.value, classinfo)):
            raise ValueError('Must be %s object' % classinfo)

    @field
    def match(self, re_):
        """Apply re.match to value."""
        if not re.match(re_, self.value):
            raise ValueError("Value not match with '%s'" % re_)

    @field
    def apply(self, func):
        """Apply function to Field(). Receive `self` as first args.

        ## Example use:
        class Model(Dictify):
        def check(self):
            # Do something with self, like checking value or setting value.

        Field().apply(check)
        """
        func(self)


class Model(dict):
    class Dict(dict):
        def __init__(self, dict_, field):
            self._field = field
            return super().__init__(dict_)

        def __setitem__(self, k, v):
            v = self._field[k]._verify(k, v)
            return super().__setitem__(k, v)

        @property
        def field(self):
            return self._field

    def __new__(cls, dict_=dict()):
        cls._field = dict()
        for k, v in vars(cls).items():
            if isinstance(v, Field):
                cls._field[k] = v.verify
                dict_[k] = v._verify(k, dict_.get(k))
        return cls.Dict(dict_, cls._field)
