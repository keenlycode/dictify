import re
import inspect
import math
import unittest
import warnings

test_case = unittest.TestCase()


class Function:
    def __init__(self, func, *args, **kw):
        """Keep `func`, `*args` and `**kw` to be called."""
        self.func = func
        self.args = args
        self.kw = kw

    def __call__(self, value):
        return self.func(value, *self.args, **self.kw)

class define:
    def value(func):
        """Decorator to add function to field if value is provided."""

        def wrapper(field, *args, **kw):
            def f(value, *args, **kw):
                if value is None or '' or []:
                    return value
                else:
                    return func(value, *args, **kw)
            function = Function(f, *args, **kw)
            field.functions.append(function)
            return field
        return wrapper

    def empty(func):
        """Decorator to add field's function if value is empty"""
        def wrapper(field, *args, **kw):
            def f(value, *argd, **kw):
                if value is None or '' or []:
                    return func(value, *args, **kw)
                else:
                    return value
            function = Function(f, *args, **kw)
            field.functions.append(function)
            return field
        return wrapper

    def any(func):
        def wrapper(field, *args, **kw):
            function = Function(func, *args, **kw)
            field.functions.append(function)
            return field
        return wrapper


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
        super().__init__(values)

    def __setitem__(self, index, value):
        test_case.assertIsInstance(value, self._type)
        return super().__setitem__(index, value)

    def append(self, value):
        test_case.assertIsInstance(value, self._type)
        return super().append(value)


class Field:

    def __init__(self):
        self.value = None
        self.functions = []

    def query(self, value):
        """Apply all functions to field's value"""
        errors = list()
        self.value = value
        for function in self.functions:
            try:
                value = function(self.value)
                if value is not None:
                    self.value = value
            except (ValueError, AssertionError) as e:
                errors.append(e.args[0])
        if errors:
            raise ValueError(errors)
        return self

    @define.value
    def any(value, members: list):
        """(Deprecated) Check if value is any of members."""
        warnings.warn('Deprecated. Changed to `anyof`', DeprecationWarning)
        test_case.assertIn(value, members)

    @define.value
    def anyof(value, members: list):
        """Check if value is any of members."""
        test_case.assertIn(value, members)

    @define.any
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

    @define.empty
    def default(value, default_):
        """Set default value."""
        if callable(default_):
            return default_()
        else:
            return default_

    @define.empty
    def required(value):
        """Required."""
        raise ValueError('Required.')

    @define.value
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

    @define.value
    def listof(values, type_=None):
        return ListOf(type_, values)

    @define.value
    def match(value, re_: 'regular expession string'):
        """Check value matching with regular expression."""
        test_case.assertRegex(value, re_)

    @define.value
    def number(value: (int, float, complex),
               min: (int, float, complex) = -math.inf,
               max: (int, float, complex) = math.inf):
        """Check if value is number"""
        if not min <= value <= max:
            raise ValueError(
                'Value is %s, must be %s to %s'
                % (value, min, max)
            )

    @define.value
    def range(value: (int, float, complex),
              min: (int, float, complex) = -math.inf,
              max: (int, float, complex) = math.inf):
        """(Deprecated) Set possible value range."""
        if not min <= value <= max:
            raise ValueError(
                'Value is %s, must be %s to %s'
                % (value, min, max)
            )

    @define.value
    def subset(values, members: list):
        """Check if value is subset of defined members."""
        test_case.assertLessEqual(set(values), set(members))

    @define.value
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

    def __init__(self, data=dict()):
        field = dict()
        errors = dict()
        result = dict()
        for k in self.__dir__():
            f = self.__getattribute__(k)
            if isinstance(f, Field):
                try:
                    field[k] = f.query(data.get(k))
                    result[k] = field[k].value
                except (ValueError, AssertionError) as error:
                    errors[k] = error

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
        self._field = field
        super().__init__(result)

    def __setitem__(self, k, v):
        """Verify value before `super().__setitem__`."""
        try:
            value = self._field[k].query(v).value
        except KeyError:
            raise KeyError('Field is not defined')

        return super().__setitem__(k, value)

    def update(self, data):
        """Modify `update` method to verify data before update."""
        errors = dict()
        for k, v in data.items():
            try:
                data[k] = self._field[k].query(v).value
            except ValueError as e:
                errors[k] = e
            except KeyError as e:
                errors[k] = KeyError('Field is not defined')
        if errors:
            raise Exception(errors)
        return super().update(data)
