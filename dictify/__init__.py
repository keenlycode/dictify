import re
import inspect
import math
import unittest
import warnings


class RuleArgsError(Exception):
    """Error exception for verify functoin arguments."""

    def __init__(self, msg):
        """Init."""
        return super().__init__(msg)


class Field:
    """Class contain function to verify Model's fields."""

    test = unittest.TestCase()

    def __init__(self):
        """Init object."""
        self.rule = Field.Rule()

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
            self.value = None
            self.rules = []
            self.errors = []

        def verify(self, key, value):
            """Verify value with rules."""
            self.value = value
            self.errors = list()
            for verify in self.rules:
                try:
                    value = verify(self.value)
                    if value:
                        self.value = value
                except (ValueError, AssertionError) as e:
                    self.errors.append(e.args[0])
            if self.errors:
                raise ValueError(self.errors)
            return self

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
        if value in [None, '']:
            raise ValueError('Required.')

    @rule_allow_none
    def default(value, default_: 'default value'):
        """Set default value."""
        if value is None:
            return default_

    @rule
    def type(value, type_: type):
        """Check value's type."""
        Field.test.assertIsInstance(value, type_)

    @rule
    def match(value, re_: 'regular expession string'):
        """Check value matching with regular expression."""
        Field.test.assertRegex(value, re_)

    @rule_allow_none
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
    def length(value: (str, list), min: int = 0, max: int = math.inf):
        """Set min/max of value's length."""
        try:
            length_ = len(value)
        except TypeError:
            raise ValueError('Value must be `list, str` type')
        if not(min <= length_ <= max):
            raise ValueError(
                'Value\'s length is %s. Must be %s to %s'
                % (length_, min, max)
            )

    @rule
    def range(value: (int, float, complex),
              min: (int, float, complex) = -math.inf,
              max: (int, float, complex) = math.inf):
        """Set possible value range."""
        if not(min <= value <= max):
            raise ValueError(
                'Value is %s, must be %s to %s'
                % (value, min, max)
            )

    @rule
    def any(value, members: list):
        """(Deprecated) Check if value is any of members."""
        warnings.warn('Deprecated. Changed to `anyof`', DeprecationWarning)
        Field.test.assertIn(value, members)

    @rule
    def anyof(value, members: list):
        """Check if value is any of members."""
        Field.test.assertIn(value, members)

    @rule
    def subset(values, members: list):
        """Check if value is subset of defined members."""
        Field.test.assertLessEqual(set(values), set(members))


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
            """Verify value before `super().__setitem__`."""
            try:
                value = self._field[k].verify(k, v).value
            except KeyError as e:
                raise KeyError('Field is not defined')
            return super().__setitem__(k, value)

        def update(self, data):
            """Modify `update` method to verify data before update."""
            errors = dict()
            for k, v in data.items():
                try:
                    data[k] = self._field[k].verify(k, v).value
                except ValueError as e:
                    errors[k] = e
                except KeyError as e:
                    errors[k] = KeyError('Field is not defined')
            if errors:
                raise Exception(errors)
            return super().update(data)

    def __new__(cls, data=dict()):
        """Create Model.Dict with field's rules."""
        rule = dict()
        errors = dict()
        result = dict()

        # Loop to find Field then verify, keep errors information.
        for k, v in vars(cls).items():
            if isinstance(v, Field):
                try:
                    rule[k] = v.rule.verify(k, data.get(k))
                    result[k] = rule[k].value
                except (ValueError, AssertionError) as e:
                    errors[k] = e

                # Delete data items() after field verification.
                try:
                    del data[k]
                # Ignore possibility when data doesn't have defined field.
                # In case when field is not required or have default value.
                except KeyError:
                    pass

        # After verification, If there's data.keys() left,
        # it means the field is not defined.
        for k in data.keys():
            errors[k] = KeyError('Field is not defined')
        if errors:
            raise Exception(errors)
        return cls.Dict(result, rule)
