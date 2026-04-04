"""dictify provides lightweight schema and validation helpers for dict data."""

from __future__ import annotations

import re
from functools import wraps
from typing import Any, Callable, cast

Validator = Callable[..., Any]
DefaultFactory = Callable[[], Any]
DataDict = dict[str, Any]


class Function:
    def __init__(self, func, *args, **kw):
        self.func = func
        self.args = args
        self.kw = kw

    def __call__(self, field, value):
        return self.func(field, value, *self.args, **self.kw)

    def __repr__(self):
        return f"{self.func.__name__}{self.args}{self.kw}"


def function(func: Validator):
    """Decorator used in Field class to add methods in validation chain"""

    @wraps(func)
    def wrapper(self, *args, **kw):
        # Test default value.
        if self.default != UNDEF:
            try:
                func(self, self.default, *args, **kw)
            except Exception as error:
                func_name = getattr(func, "__name__", type(func).__name__)
                raise Field.DefineError(
                    f"Field(default={self.default}) conflict with ",
                    f"{func_name}(*{args}, **{kw})",
                    error,
                )

        # Keep function in chain.
        self._functions.append(Function(func, *args, **kw))
        return self

    return wrapper


class _UNDEF:
    """Create ```UNDEF`` value"""

    def __repr__(self):
        return "UNDEF"


UNDEF = _UNDEF()


class ListOf(list):
    """Modified list which check it's members instance.

    Parameters
    ----------
    value:
        Value for validation it's type with ``type_``.
    type_:
        Type for validation with ``value``
    """

    class ValueError(Exception):
        pass

    def __init__(
        self,
        values,
        type_: Any = UNDEF,
        validate: Validator | None = None,
    ):
        if isinstance(type_, type):
            self.types = (type_,)
        else:
            self.types = type_

        self.validate_func = validate

        if self.types[0] == UNDEF:
            return super().__init__(values)

        for value in values:
            self._validate(value)

        return super().__init__(values)

    def __setitem__(self, index, value):
        """Set list value at ``index`` if ``value`` is valid"""

        self._validate(value)
        return super().__setitem__(index, value)

    def _validate(self, value):
        if self.types[0] == UNDEF:
            return
        if isinstance(value, dict):
            models = filter(lambda type_: isinstance(type_, Model), self.types)
            for model_cls in models:
                try:
                    model_cls(value)
                    return
                except Exception:
                    pass
        assert isinstance(value, self.types), (
            f"'{value}' is not instance of {self.types}"
        )

        if callable(self.validate_func):
            self.validate_func(value)

    def append(self, value):
        """Append object to the list if ``value`` is valid."""

        self._validate(value)
        return super().append(value)

    def list(self):
        """Return data as native `list`"""

        data = []
        for item in self:
            if isinstance(item, Model):
                data.append(item.dict())
            elif isinstance(item, ListOf):
                data.append(item.list())
            else:
                data.append(item)
        return data


class Field:
    """Create ``Field()`` object which can validate it's value.
    Can be defined in class ``Model``.

    Examples
    --------
    ::

        # Use with validators.
        field = Field(required=True).anyof(['AM','PM'])
        field.value = 'AM'
        field.value = 'A'  # This will raise Field.VerifyError

        # Chained validators.
        field = Field(default=0).instance(str).search('.*@.*)
        field.value = 'user@somewhere.com'; # OK
        field.value = 1  # This will raise Field.VerifyError

    Notes
    -----
        As the examples, when defining ``Field()`` validation with
        it's methods below. The first arguments ``(value)`` can be omitted
        since it will be put automatically while validating value.
    ...

    Parameters
    ----------
    required: bool=False
        Required option. If set to ``True``, call ``Field().value`` without
        assigned value will raise ``Field.RequiredError``
    default: any=UNDEF
        Field's default value
    grant: list
        Granted values which always valid.
    """

    class VerifyError(Exception):
        """Error to be raised if ``Field().value`` doesn't pass validation."""

        pass

    class RequiredError(Exception):
        """Error to be raised if ``Field(required=True)``
        but no value provided.
        """

        pass

    class DefineError(Exception):
        """Error to be raised when defining ``Field()``."""

        pass

    def __init__(self, required: bool = False, default=UNDEF, grant=None):
        self.required = required
        self._default = default
        if grant is None:
            grant = []
        assert isinstance(grant, list)
        self.grant = grant
        self._functions = list()
        self._value = self.default

    def clone(self):
        """Return a fresh field instance with the same validation definition."""

        field = type(self)(
            required=self.required,
            default=self._default,
            grant=self.grant.copy(),
        )
        field._functions = self._functions.copy()
        return field

    @property
    def default(self):
        """Field's default value"""
        if callable(self._default):
            default_factory = cast(DefaultFactory, self._default)
            return default_factory()
        return self._default

    @property
    def value(self):
        """``Field()``'s value
        - Required Field will raise RequiredError if ask for value
          before assigned.
        """

        if self.required and self._value == UNDEF:
            raise Field.RequiredError("Field is required")

        return self._value

    @value.setter
    def value(self, value):
        """Set field's value
        - Verify value by field's functions
        - Set fields' value if function return value
        """
        errors = list()
        if self.required and value == UNDEF:
            raise Field.RequiredError("Field is required")
        if value in self.grant:
            self._value = value
            return

        for function in self._functions:
            try:
                value_ = function(self, value)
                if isinstance(value_, (ListOf, Model)):
                    value = value_
            except Exception as e:
                errors.append((function, e))
        if errors:
            raise Field.VerifyError(errors)
        self._value = value

    def reset(self):
        """Reset ``Field().value`` to default or ``UNDEF``"""
        self._value = self.default

    @function
    def instance(self, value, type_: type):
        """Verify that ``value`` is instance to ``type_``

        ``assert isinstance(value, type_)``
        """
        assert isinstance(value, type_), f"{type(value)} is not instance of {type_}"

    @function
    def listof(
        self,
        value: Any,
        type_: Any = UNDEF,
        validate: Validator | None = None,
    ):
        """Verify list instance"""
        return ListOf(value, type_, validate)

    @function
    def match(self, value, re_: str, flags=0):
        """Match value with regular expression string ``re_``."""
        assert re.match(re_, value, flags), (
            f"Matching with re.match('{re_}', '{value}') is None"
        )

    @function
    def model(self, value, model_cls: type[Model]):
        """Verify that value pass ``model_cls`` validation."""
        return model_cls(value)

    @function
    def search(self, value, re_: str, flags=0):
        """Search value with with regular expression string ``re_``."""
        assert re.search(re_, value, flags), (
            f"Searching with re.search('{re_}', '{value}') is None"
        )

    @function
    def verify(self, value, func, message=None):
        """Designed to use with ``lambda`` for simple syntax since ``lambda``
        can't use ``assert`` statement.

        The callable must return ``True`` or ``False``.

        If return ``False``, It will be raised as ``AssertionError``.
        """
        assert func(value), message

    @function
    def func(self, value, fn):
        """Use callable function to validate value."""
        fn(value)


class Model(dict):
    """Modified ``dict`` that can defined ``Field`` in it's class."""

    class Error(Exception):
        """``Exception`` when data doesn't pass ``Model`` validation."""

        pass

    @classmethod
    def _declared_fields(cls):
        fields = {}
        for base in reversed(cls.__mro__):
            for key, value in vars(base).items():
                if isinstance(value, Field):
                    fields[key] = value
        return fields

    def __init__(self, data: DataDict | None = None, strict: bool = True):
        if data is None:
            data = {}
        assert isinstance(data, dict), "Model initial data should be instance of dict"
        assert isinstance(strict, bool)
        data = data.copy()
        self._field = {
            key: field.clone() for key, field in self._declared_fields().items()
        }
        self._strict = strict
        for key, field in self._field.items():
            if (field.default != UNDEF) and (key not in data):
                data[key] = field.value
            elif field.required:
                if key not in data:
                    raise Model.Error(
                        {key: Field.RequiredError("This field is required")}
                    )
        data = self._validate(data)
        super().__init__(data)
        self.post_validate()

    def __delitem__(self, key):
        """Delete item but also check for Field's default or required option."""

        if (key not in self._field) and (self._strict is False):
            super().__delitem__(key)
            self.post_validate()
            return

        if self._field[key].default != UNDEF:
            self[key] = self._field[key].default
        elif self._field[key].required:
            raise Model.Error({key: Field.RequiredError("Field is required")})
        else:
            super().__delitem__(key)
        self.post_validate()

    def __setitem__(self, key, value):
        """Set ``value`` if is valid."""

        error = None
        if (key not in self._field) and (self._strict is False):
            super().__setitem__(key, value)
            self.post_validate()
            return

        try:
            self._field[key].value = value
            super().__setitem__(key, self._field[key].value)
        except KeyError:
            error = {key: KeyError("Field is not defined")}
        except (Field.VerifyError, ListOf.ValueError) as e:
            error = {key: e}
        if error:
            raise Model.Error(error)
        self.post_validate()

    def _validate(self, data: DataDict):
        error = dict()
        for key in data:
            if (key not in self._field) and (self._strict is False):
                continue

            try:
                self._field[key].value = data[key]
                data[key] = self._field[key].value
            except KeyError:
                if self._strict:
                    error[key] = KeyError("Field is not defined")
            except Field.VerifyError as e:
                error[key] = e
        if error:
            raise Model.Error(error)
        return data

    def pop(self, *args, **kw):
        raise NotImplementedError

    def popitem(self, *args, **kw):
        raise NotImplementedError

    def post_validate(self):
        pass

    def update(self, data=None, **kwargs):
        """Update ``data`` if is valid."""
        if data is None:
            data = {}
        data = dict(data, **kwargs)
        data = self._validate(data)
        super().update(data)
        self.post_validate()

    def dict(self):
        """Return data as native `dict` and `list`"""
        data = {}
        for key, value in self.items():
            if isinstance(value, Model):
                data[key] = value.dict()
            elif isinstance(value, ListOf):
                data[key] = value.list()
            else:
                data[key] = value
        return data
