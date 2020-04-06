import math
import re
import typing
from functools import wraps


def function(func: typing.Callable):
    """Decorator to add ``Field`` methods for value validation."""
    @wraps(func)
    def wrapper(field, *args, **kw):
        if field._value != UNDEF:  # There's a default value.
            try:
                func(field, field._value, *args, **kw)
            except AssertionError as error:
                raise FieldDefineError(
                    f"Field(default={field._value}) conflict with "+\
                    f"{func.__name__}(*{args}, **{kw})", error)
        field._functions.append(
            lambda field, value: func(field, value, *args, **kw))
        return field
    return wrapper


class Undef:
    def __repr__(self):
        return 'undef'


#: undefined value for using with ``Field.__init__()``
UNDEF = Undef()


class ModelError(Exception):
    """``Exception`` when data doesn't pass ``Model`` validation.

    Parameters
    ----------
    message: str
        Error message. Format: ``{'field': FieldError([Exception,])}``
    """
    pass


class FieldError(Exception):
    """``Exception`` when data doesn't pass ``Field`` validation.

    Parameters
    ----------
    message: str
        Error message. Format: ``FieldError([Exception,])``
    """
    pass


class FieldDefineError(Exception):
    pass


class ListError(Exception):
    """
    ListError message format:
    ListError([Exception,])
    """
    pass


class ListOf(list):
    """Modified list to check it's members instance.

    Parameters
    ----------
    value:
        Value for validation it's type with ``type_``.
    type_:
        Type for validation with ``value``
    """
    def __init__(self, value, type_):
        self._type = type_
        errors = list()
        for v in value:
            if not isinstance(v, self._type):
                errors.append(
                    AssertionError(f"'{v}' is not instance of {self._type}")
                )
        if errors:
            raise ListError(errors)
        super().__init__(value)

    def __setitem__(self, index, value):
        """Set list value at ``index`` if ``value`` is valid"""
        assert isinstance(value, self._type),\
            f"'{value}' is not instance of {self._type}"
        return super().__setitem__(index, value)

    def append(self, value):
        """Append object to the end of the list if ``value`` is valid."""
        assert isinstance(value, self._type),\
            f"'{value}' is not instance of {self._type}"
        return super().append(value)


class Field:
    """Create ``Field()`` object which can validate it's value.
    Can be defined in ``class Model``.

    Examples
    --------
    ::

        # Use with validators.
        field = Field(required=True).anyof(['AM','PM'])
        field.value = 'AM'
        field.value = 'A'  # This will raise FieldError

        # Chained validators.
        field = Field(default=0).instance(int).min(0).max(10)
        field.value = 5
        field.value = -1  # This will raise FieldError

    Notes
    -----
        As the examples, when defining ``Field()`` validation with it's methods
        below. The first arguments ``(value)`` can be omitted since it will be
        put automatically while validating value.
    ...

    Parameters
    ----------
    required: bool=False
        Required option. Only useful when define ``Field()`` in ``Model`` class
    disallow: list=[None]
        List of disallowed value.
    default: any
        Default value. Ignore required option if set.
    """

    def __init__(self, required: bool = False,
                 disallow: list = [None], **option):
        self._functions = list()
        self.option = option
        self._value = UNDEF
        self.option['required'] = required
        self.option['disallow'] = disallow
        if 'default' in self.option:
            assert self.option['default'] not in self.option['disallow'],\
                f"""Default value is disallowed.
                default({self.option['default']}), disallow({self.option['disallow']})
                """
            self._value = self.option['default']

    @property
    def value(self):
        """``Field()``'s value"""
        return self._value

    @value.setter
    def value(self, value):
        errors = list()
        if value in self.option['disallow']:
            raise FieldError([
                AssertionError(
                    f"""Value({value}) is not allowed.
                    Disallow {self.option['disallow']}""")
            ])
        for function in self._functions:
            try:
                function(self, value)
            except AssertionError as e:
                errors.append(e)
        if errors:
            raise FieldError(errors)
        self._value = value

    @function
    def anyof(self, value, members: list):
        """``assert value in members``"""
        assert value in members, f'{value} is not in {members}'

    @function
    def func(self, value, fn):
        """Use custom function for value validation.

        - ``fn`` should have call signature as ``fn(field, value)``
        - ``fn`` should raise ``AssertionError`` if value doesn't pass validation.

        Examples
        --------
        ::

            def is_uuid4(field, value):
                id = uuid.UUID(value)
                assert id.version == 4

            field = Field().func(is_uuid4)
        """
        fn(self, value)

    @function
    def instance(self, value, type_: type):
        """``assert isinstance(value, type_)``"""
        assert isinstance(value, type_),\
            f'{type(value)} is not instance of {type_}'

    @function
    def length(self, value, min: int = 0, max: int = math.inf):
        """Set value's min/max length. ``assert min <= len(value) <= max``"""
        assert isinstance(value, (str, list)),\
            f"{value} is not instance of `str` or `list`"
        length_ = len(value)
        assert min <= length_ <= max,\
            f"Value's length is {length_}. Must be {min} to {max}"

    @function
    def listof(self, value, type_):
        """Check if ``Field()`` value is a list of ``type_``"""
        ListOf(value, type_)

    @function
    def max(self, value, max_: typing.Union[int, float, complex] = -math.inf, equal=True):
        """
        - If ``equal`` == ``True``, Check if ``value`` <= ``max_``
        - If ``equal`` == ``False``, Check if ``value`` < ``max_``
        """
        if equal is True:
            assert value <= max_,\
                f"Value({value}) <= Max({max_}) is False"
        else:
            assert value < max_,\
                f"Value({value}) < Max({max_}) is False"

    @function
    def min(self, value, min_: typing.Union[int, float, complex] = -math.inf, equal=True):
        """
        - If ``equal`` == ``True``, Check if ``value`` >= ``min_``
        - If ``equal`` == ``False``, Check if ``value`` > ``min_``
        """
        if equal is True:
            assert value >= min_,\
                f"Value({value}) >= Min({min_}) is False"
        else:
            assert value > min_,\
                f"Value({value}) > Min({min_}) is False"

    @function
    def model(self, value, model_cls: 'Model'):
        """Check if value pass validation by ``model_cls``.
        Useful for nested data."""
        model_cls(value)

    @function
    def search(self, value, re_: str):
        """Check value matching with regular expression string ``re_``."""
        assert re.search(re_, value),\
            f"re.search('{re_}', '{value}') is None"

    @function
    def subset(self, value, members: list):
        """Check if value is subset of ``members``."""
        assert set(value) <= set(members),\
            f"{value} is not a subset of {members}"


class Model(dict):
    """Modified ``dict`` that can defined ``Field`` in it's class.

    Examples
    --------
    ::

        class Note(Model):
            title = Field(required=True).instance(str)
            content = Field().instance(str)
            datetime = Field(default=datetime.utcnow()).instance(datetime)

        note = Note({'title': 'Title'})

    Parameters
    ----------
    data: dict
        Model's data
    """

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
        self._validate(data)
        super().__init__(data)

    def __delitem__(self, key):
        """Delete item but also check for Field's default or required option
        to make sure that Model's data is valid.
        """
        if 'default' in self._field[key].option:
            self[key] = self._field[key].option['default']
        elif self._field[key].option.get('required'):
            raise ModelError({key: KeyError("This field is required")})
        else:
            return super().__delitem__(key)

    def __setitem__(self, key, value):
        """Set item's value if ``value`` is valid."""
        error = None
        try:
            self._field[key].value = value
            super().__setitem__(key, self._field[key].value)
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
            except KeyError:
                error[key] = KeyError('Field is not defined')
            except FieldError as e:
                error[key] = e
        if error:
            raise ModelError(error)

    def update(self, data):
        """Update data if ``data`` is valid."""
        assert isinstance(data, dict)
        self._validate(data)
        super().update(data)
