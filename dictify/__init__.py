import re
import inspect
import math


class Field:
    """Class contain function to verify Model's fields."""

    def __init__(self):
        """Init object."""
        self.rule = Field.Rule()

    def rule(func):
        """Decorate function to add a rule. Bypassed if value is `None`."""
        def wrapper(self, *args, **kw):
            def f(value, *args, **kw):
                if value is None:
                    return value
                else:
                    return func(value, *args, **kw)
            verify = Field.Verify(f, *args, **kw)
            self.rule.rules.append(verify)
            return self
        return wrapper

    def rule_allow_none(func):
        """Decorate function to add a rule."""
        def wrapper(self, *args, **kw):
            verify = Field.Verify(func, *args, **kw)
            self.rule.rules.append(verify)
            return self
        return wrapper

    @rule_allow_none
    def required(value):
        """Required."""
        if (value is None) or (value == ''):
            raise ValueError('Required')

    @rule_allow_none
    def default(value, default: 'default value'):
        """Set default value."""
        if value is None:
            return default

    @rule
    def type(value, classinfo: 'class'):
        """Check value's type."""
        if not(isinstance(value, classinfo)):
            raise ValueError('Must be %s object' % classinfo)

    @rule
    def match(value, re_: 'regular expession string'):
        """Check value matching with regular expression."""
        if not re.match(re_, value):
            raise ValueError("Value not match with '%s'" % re_)

    @rule
    def apply(value, func: 'function to apply'):
        """Apply function to Field().

        ## Example use:
        class User(Model):
            def check(value):
                # Do something with value,
                # like checking value or setting value.

            name = Field().apply(check)
        """
        return func(value)

    @rule
    def size(value, min=0, max=math.inf):
        """Set min/max of value size."""
        try:
            size = len(value)
        except TypeError:
            raise ValueError('Can\'t find size by `len()``')
        if not(min <= size <= max):
            raise ValueError(
                'Value size is %s, must be %s to %s'
                % (size, min, max)
            )

    @rule
    def range(value, min, max):
        """Set possible value length."""
        if not(min <= value <= max):
            raise ValueError(
                'Value is %s, must be %s to %s'
                % (value, min, max)
            )

    class Verify:
        """Class contain verify function to be called."""

        def __init__(self, func, *args, **kw):
            """Keep `func`, `*args` and `**kw` to be called."""
            self.func = func
            self.args = args
            self.kw = kw

        def __call__(self, value):
            """Verify value with `self.func`."""
            return self.func(value, *self.args, **self.kw)

    class Rule:
        """Class for verify rules. Store rules and errors information."""

        def __init__(self):
            """Init rule object."""
            self.rules = []
            self.errors = []

        def verify(self, key, value):
            """Verify value with rules."""
            self.value = value
            self.errors = list()
            for verify in self.rules:
                try:
                    value = verify(value)
                    if value:
                        self.value = value
                except ValueError as e:
                    self.errors.append(e.args[0])
            if self.errors:
                raise ValueError("'%s' : %s" % (key, self.errors))
            return self


class Model(dict):
    """Class to defined fields and rules.

    ## Example:
    Class User(Model):
        name = Field().required().type(str)

    user = User({'name': 'John'})
    """

    class Dict(dict):
        """Modified `dict` to strict with field's rules."""

        def __init__(self, data, rule):
            """Create modified dict from data.

            Dict() object will keep Field.Rule() object in self._field
            which will be called in `__setitem__`
            """
            self._field = rule
            return super().__init__(data)

        def __setitem__(self, k, v):
            """Verify value before set value."""
            self._field[k].verify(k, v)
            return super().__setitem__(k, v)

    def __new__(cls, data=dict()):
        """Create Model.Dict with field's rules."""
        rule = dict()
        for k, v in vars(cls).items():
            if isinstance(v, Field):
                rule[k] = v.rule.verify(k, data.get(k))
                data[k] = rule[k].value
        return cls.Dict(data, rule)
