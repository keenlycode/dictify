import math
import re


def function(func):
    """Decorator to add function to Field()._functions for validation."""
    def wrapper(field, *args, **kw):
        field._functions.append(lambda field: func(field, *args, **kw))
        return field
    return wrapper


class ModelError(Exception):
    """
    ModelError message format:
    {'field_name': FieldError(Exceptions)}
    """
    pass


class FieldError(Exception):
    """
    FieldError message format:
    FieldError(Exceptions)
    """
    pass


class ListError(Exception):
    """
    ListError message format
    ListError(Exceptions)
    """
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

    def validate(self, value=None):
        """Apply all functions to field's value"""
        errors = list()
        self.value = self._default
        if value is not None:
            self.value = value
        if self._required:
            try:
                assert self.value, 'Value is required'
            except AssertionError as e:
                raise FieldError([e])
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

    @function
    def type(self, type_):
        assert isinstance(self.value, type_), f'Value is not instance of {type_}'

    @function
    def anyof(self, members: list):
        """Check if value is any of members."""
        assert self.value in members, f'{self.value} is not in {members}'

    @function
    def length(self, min: int = 0, max: int = math.inf):
        """Set min/max of value's length."""
        assert isinstance(self.value, (str, list)),\
            f"Value muse be `str` or `list` object"
        length_ = len(self.value)
        assert min <= length_ <= max,\
            f"Value's length is {length_}. Must be {min} to {max}"

    @function
    def listof(self, type_):
        self.value = ListOf(self, type_)

    @function
    def model(self, cls):
        self.value = cls(self.value)

    @function
    def search(self, re_: str):
        """Check value matching with regular expression."""
        assert re.search(re_, self.value),\
            f"re.search('{re_}', '{self.value}') is None"

    @function
    def min(self, min_: (int, float, complex) = -math.inf, equal=True):
        if equal is True:
            assert self.value >= min_,\
                f"Value({self.value}) >= Min({min_})"
        else:
            assert self.value > min_,\
                f"Value({self.value}) > Min({min_})"

    @function
    def max(self, max_: (int, float, complex) = -math.inf, equal=True):
        if equal is True:
            assert self.value <= max_,\
                f"Value({self.value}) <= Max({max_})"
        else:
            assert self.value < max_,\
                f"Value({self.value}) < Max({max_})"

    @function
    def subset(self, members: list):
        """Check if value is subset of defined members."""
        assert set(self.value) <= set(members),\
            f"{self.value} is not a subset of {members}"

    @function
    def verify(self, func):
        func(self)


class Model(dict):
    """Class to defined fields and rules."""

    def __init__(self, data=dict()):
        assert isinstance(data, dict),\
            f"Model initial data should be an instance of `dict`"
        data = data.copy()
        field = dict()
        for key in self.__dir__():
            item = self.__getattribute__(key)
            # Set field[key] if It's Model or Field instance.
            # If it's Field instance, check for default value
            if isinstance(item, Field):
                field[key] = item
                if (data.get(key) is None) and (item._default is not None):
                    data[key] = item._default
            if isinstance(item, Model):
                field[key] = item

        self._field = field
        data = self._validate(data)
        super().__init__(data)

    def __setitem__(self, key, value):
        """Verify value before `super().__setitem__`."""
        error = None
        try:
            self._field[key].validate(value)
            super().__setitem__(key, value)
        except KeyError:
            error = {key: KeyError('Field is not defined')}
        except (FieldError, ListError) as e:
            error = {key: e}
        if error:
            raise ModelError(error)

    def _validate(self, data: dict):
        error = dict()
        for key in data:
            try:
                data[key] = self._field[key].validate(data[key]).value
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
