import re
import inspect
import math
import unittest
import warnings

test_case = unittest.TestCase()

class ListOf(list):
    def __init__(self, type_=None, values=[]):
        self._type = type_
        errors = list()
        for v in values:
            try:
                test_case.assertIsInstance(v, self._type)
            except AssertionError as e:
                errors.append(e)
        if errors:
            raise ValueError(errors)
        return super().__init__(values)

    def __setitem__(self, index, value):
        test_case.assertIsInstance(value, self._type)
        return super().__setitem__(index, value)

    def append(self, value):
        test_case.assertIsInstance(value, self._type)
        return super().append(value)

class Field:
    """Class contain function to verify Model's fields."""

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

    def field(func):
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

    def field_with_none(func):
        """Decorate function to add a rule."""
        def wrapper(self, *args, **kw):
            verify = Field.Verify(func, *args, **kw)
            self.rule.rules.append(verify)
            return self
        return wrapper

    @field_with_none
    def default(value, default_: 'default value'):
        """Set default value."""
        if value is None:
            return default_

    @field_with_none
    def required(value):
        """Required."""
        if value in [None, '', []]:
            raise ValueError('Required.')

    @field
    def any(value, members: list):
        """(Deprecated) Check if value is any of members."""
        warnings.warn('Deprecated. Changed to `anyof`', DeprecationWarning)
        test_case.assertIn(value, members)

    @field
    def anyof(value, members: list):
        """Check if value is any of members."""
        test_case.assertIn(value, members)

    @field_with_none
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

    @field
    def length(value: (str, list), min: int = 0, max: int = math.inf):
        """Set min/max of value's length."""
        try:
            length_ = len(value)
        except TypeError:
            raise ValueError('Value must be `list, str` type')
        if not min <= length_ <= max:
            raise ValueError(
                'Value\'s length is %s. Must be %s to %s'
                % (length_, min, max)
            )

    @field
    def listof(values, type_=None):
        return ListOf(type_, values)

    @field
    def match(value, re_: 'regular expession string'):
        """Check value matching with regular expression."""
        test_case.assertRegex(value, re_)

    @field
    def number(value: (int, float, complex),
               min: (int, float, complex) = -math.inf,
               max: (int, float, complex) = math.inf):
        """Check if value is number"""
        if not min <= value <= max:
            raise ValueError(
                'Value is %s, must be %s to %s'
                % (value, min, max)
            )

    @field
    def range(value: (int, float, complex),
              min: (int, float, complex) = -math.inf,
              max: (int, float, complex) = math.inf):
        """(Deprecated) Set possible value range."""
        if not min <= value <= max:
            raise ValueError(
                'Value is %s, must be %s to %s'
                % (value, min, max)
            )

    @field
    def subset(values, members: list):
        """Check if value is subset of defined members."""
        test_case.assertLessEqual(set(values), set(members))

    @field
    def type(value, type_: type):
        """Check value's type."""
        test_case.assertIsInstance(value, type_)


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
