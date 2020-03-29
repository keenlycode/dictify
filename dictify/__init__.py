import math
import re


def rule(func):
    """Decorator to add function to field for validation."""
    def wrapper(field, *args, **kw):
        field._functions.append(lambda field: func(field, *args, **kw))
        return field
    return wrapper


class ModelError(Exception):
    pass


class FieldError(Exception):
    pass


class ListError(Exception):
    pass


class ListOf(list):
    def __init__(self, field, type_=None):
        self._type = type_
        errors = list()
        for v in field.value:
            try:
                assert isinstance(v, self._type),\
                    f"'{v}' is not instance of {self._type}"
            except AssertionError as e:
                errors.append(e)
        if errors:
            raise ListError(errors)
        super().__init__(field.value)

    def __setitem__(self, index, value):
        assert isinstance(value, self._type),\
            f"'{value}' is not instance of {self._type}"
        return super().__setitem__(index, value)

    def append(self, value):
        assert isinstance(value, self._type),\
            f"'{value}' is not instance of {self._type}"
        return super().append(value)


class Field:
    def __init__(self, required=False, default=None):
        self._required = required
        self._default = default
        self._functions = list()
        self.value = default

    def _validate(self, value=None):
        """Apply all functions to field's value"""
        errors = list()
        if value is not None:
            self.value = value
        else:
            self.value = self._default
        if self._required:
            assert self.value is not None, 'Value is required'
        if self.value is None:
            return self
        for function in self._functions:
            try:
                function(self)
            except AssertionError as e:
                errors.append(e)
        if errors:
            raise FieldError(errors)
        return self

    @rule
    def type(self, type_):
        assert isinstance(self.value, type_), f'Value is not instance of {type_}'

    @rule
    def anyof(self, members: list):
        """Check if value is any of members."""
        assert self.value in members, f'{self.value} is not in {members}'

    @rule
    def length(self, min: int = 0, max: int = math.inf):
        """Set min/max of value's length."""
        assert isinstance(self.value, (str, list)),\
            f"Value muse be `str` or `list` object"
        length_ = len(self.value)
        assert min <= length_ <= max,\
            f"Value's length is {length_}. Must be {min} to {max}"

    @rule
    def listof(self, type_):
        self.value = ListOf(self, type_)

    @rule
    def verify(self, func):
        func(self)

    @rule
    def search(self, re_: str):
        """Check value matching with regular expression."""
        assert re.search(re_, self.value)

    @rule
    def min(self, min_: (int, float, complex) = -math.inf, equal=True):
        if equal is True:
            assert self.value >= min_, f"{self.value} => {min_}"
        else:
            assert self.value > min_, f"{self.value} > {min_}"

    @rule
    def max(self, max_: (int, float, complex) = -math.inf, equal=True):
        if equal is True:
            assert self.value <= max_, f"{self.value} <= {max_}"
        else:
            assert self.value < max_, f"{self.value} < {max_}"

    @rule
    def subset(self, members: list):
        """Check if value is subset of defined members."""
        assert set(self.value) <= set(members),\
            f"{self.value} is not a subset of {members}"


class Model(dict):
    """Class to defined fields and rules."""

    def __init__(self, data=dict()):
        assert isinstance(data, dict)
        field = dict()
        for key in self.__dir__():
            f = self.__getattribute__(key)
            if not isinstance(f, Field):
                continue
            field[key] = f
        self._field = field
        data = self._validate(data.copy())
        super().__init__(data)

    def __setitem__(self, key, value):
        """Verify value before `super().__setitem__`."""
        try:
            self._field[key]._validate(value)
            super().__setitem__(key, value)
        except KeyError:
            raise KeyError('Field is not defined')

    def _validate(self, data: dict):
        error = dict()
        for key in data:
            try:
                data[key] = self._field[key]._validate(data[key]).value
            except KeyError:
                error[key] = KeyError('Field is not defined')
            except FieldError as e:
                error[key] = e
        if error:
            raise ModelError(error)
        return data

    def update(self, data):
        assert isinstance(data, dict)
        data = self._validate(data.copy())
        super().update(data)
