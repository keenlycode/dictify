import math
import re
from functools import wraps


def function(func):
    """Decorator to add function to Field()._functions for validation."""
    @wraps(func)
    def wrapper(field, *args, **kw):
        field._functions.append(lambda field: func(field, *args, **kw))
        return field
    return wrapper


class ModelError(Exception):
    """
    ModelError message format:
    {'field': FieldError([Exception,])}
    """
    pass


class FieldError(Exception):
    """
    FieldError message format:
    FieldError([Exception,])
    """
    pass


class ListError(Exception):
    """
    ListError message format
    ListError([Exception,])
    """
    pass


class ListOf(list):
    """
    Modified list to check it's members instance.
    """
    def __init__(self, field, type_=None):
        self._type = type_
        errors = list()
        for v in field.value:
            if not isinstance(v, self._type):
                errors.append(
                    AssertionError(f"'{v}' is not instance of {self._type}")
                )
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
    """Create ``Field()`` object which can validate it's value.

    ``Field()`` is designed to be defined in ``Model`` class,
    so it's not much useful for standalone usage. See ``Model`` for more
    information and usage

    Examples
    --------
    ::

        # Use with options.
        field = Field(required=True, disallow=[None])
        value = 'hi'
        field.validate(value)
        field.value = value

        # Use with validators.
        field = Field().anyof(['AM','PM'])
        value = 'AM'
        field.validate(value)
        field.value = value

    Parameters:
        required(bool=False): Required option.
            Only useful when define ``Field()`` in ``Model`` class
        disallow(list=[None]): List of disallowed value.
        default(any): Default value. Ignore required option if set.
    """
    def __init__(self, required: bool = False,
                 disallow: list = [None], **option):
        self._functions = list()
        self._value = None
        self.option = option
        self.option['required'] = required
        self.option['disallow'] = disallow
        if 'default' in self.option:
            assert self.option['default'] not in self.option['disallow'],\
                f"""Default value is disallowed.
                default({self.option['default']}), disallow({self.option['disallow']})
                """

    @property
    def value(self):
        """``Field()`` value"""
        return self._value

    @value.setter
    def value(self, value):
        self._validate(value)
        self._value = value

    def _validate(self, value=None):
        """Validate field's value"""
        errors = list()
        if value in self.option['disallow']:
            raise FieldError([
                AssertionError(
                    f"""Value({value}) is not allowed.
                    Disallow {self.option['disallow']}""")
            ])
        old_value = self.value
        self._value = value
        for function in self._functions:
            try:
                function(self)
            except AssertionError as e:
                errors.append(e)
        if errors:
            self._value = old_value
            raise FieldError(errors)

    @function
    def instance(self, type_: type):
        """``assert isinstance(self.value, type_)``"""
        assert isinstance(self.value, type_),\
            f'{type(self.value)} is not instance of {type_}'

    @function
    def anyof(self, members: list):
        """``assert self.value in members``"""
        assert self.value in members, f'{self.value} is not in {members}'

    @function
    def length(self, min: int = 0, max: int = math.inf):
        """Set value's min/max length. ``assert min <= len(self.value) <= max``"""
        assert isinstance(self.value, (str, list)),\
            f"Value muse be `str` or `list` object"
        length_ = len(self.value)
        assert min <= length_ <= max,\
            f"Value's length is {length_}. Must be {min} to {max}"

    @function
    def listof(self, type_):
        """Check if ``Field()`` value is list of ``type_``"""
        ListOf(self, type_)

    @function
    def model(self, model_cls):
        model_cls(self.value)

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
    def search(self, re_: str):
        """Check value matching with regular expression."""
        assert re.search(re_, self.value),\
            f"re.search('{re_}', '{self.value}') is None"

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
            f"Model initial data shold be instance of dict"
        data = data.copy()
        self._field = dict()
        for key in self.__dir__():
            field = self.__getattribute__(key)
            # Check if item is Field().
            if not isinstance(field, Field):
                continue
            # If default option is set in Field(), set default value
            if ('default' in field.option) and (key not in data):
                data[key] = field.option['default']
            # If required option is set in Field(), check if it's provided.
            elif field.option['required']:
                if key not in data:
                    raise ModelError({
                        key: KeyError("This field is required")
                    })
            # Keep Field() in self._field for data validation.
            self._field[key] = field
        data = self._validate(data)
        super().__init__(data)

    def __delitem__(self, key):
        if self._field[key].option.get('default'):
            self[key] = self._field[key].option['default']
        elif self._field[key].option['required']:
            raise ModelError({key: KeyError("This field is required")})
        else:
            return super().__delitem__(key)

    def __setitem__(self, key, value):
        """Verify value before `super().__setitem__`."""
        error = None
        try:
            self._field[key].value = value
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
                self._field[key].value = data[key]
                data[key] = self._field[key].value
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
        return super().update(data)
