"""Field definitions and list validation helpers for dictify."""

from __future__ import annotations

import re
from functools import wraps
from typing import TYPE_CHECKING, Any, Self, cast, overload

from ._sentinel import UNDEF
from ._types import DefaultFactory, T, Validator
from ._utils import _validate_type_spec

if TYPE_CHECKING:
    from ._model import Model


class Function:
    """Wrap a validator plus its bound arguments for deferred field validation."""

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
        if self.has_default:
            default = self.get_default()
            try:
                func(self, default, *args, **kw)
            except Exception as error:
                func_name = getattr(func, "__name__", type(func).__name__)
                raise Field.DefineError(
                    f"Field(default={default}) conflict with ",
                    f"{func_name}(*{args}, **{kw})",
                    error,
                )

        # Keep function in chain.
        self._functions.append(Function(func, *args, **kw))
        return self

    return wrapper


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
        if type_ is UNDEF:
            self.types = (UNDEF,)
        elif isinstance(type_, type):
            self.types = (type_,)
        else:
            self.types = type_

        self.validate_func = validate

        if self.types[0] is UNDEF:
            return super().__init__(values)

        for value in values:
            self._validate(value)

        return super().__init__(values)

    def __setitem__(self, index, value):
        """Set list value at ``index`` if ``value`` is valid"""

        self._validate(value)
        return super().__setitem__(index, value)

    def _validate(self, value):
        from ._model import Model

        if self.types[0] is UNDEF:
            return
        if isinstance(value, dict):
            model_types = tuple(
                cast(type[Model], type_)
                for type_ in self.types
                if isinstance(type_, type) and issubclass(type_, Model)
            )
            for model_cls in model_types:
                try:
                    model_cls(value)
                    return
                except Exception:
                    pass

        runtime_types = tuple(type_ for type_ in self.types if isinstance(type_, type))
        assert isinstance(value, runtime_types), (
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

        from ._model import Model

        data = []
        for item in self:
            if isinstance(item, Model):
                data.append(item.dict())
            elif isinstance(item, ListOf):
                data.append(item.list())
            else:
                data.append(item)
        return data


class Field[T]:
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
        self._annotation_type = UNDEF
        self._instance_type = UNDEF
        self._name: str | None = None
        self._value = self.default

    def __set_name__(self, owner, name):
        self._name = name

    def clone(self) -> Self:
        """Return a fresh field instance with the same validation definition."""

        field = type(self)(
            required=self.required,
            default=self._default,
            grant=self.grant.copy(),
        )
        field._functions = self._functions.copy()
        field._annotation_type = self._annotation_type
        field._instance_type = self._instance_type
        return field

    def _runtime_type_spec(self):
        if self._instance_type is not UNDEF:
            return self._instance_type
        return self._annotation_type

    def _validate_runtime_type(self, value):
        return _validate_type_spec(value, self._runtime_type_spec())

    def _ensure_default_matches_type_spec(self, type_spec):
        if self.has_default is False:
            return
        default = self.get_default()
        try:
            _validate_type_spec(default, type_spec)
        except Exception as error:
            raise Field.DefineError(
                f"Field(default={default}) conflict with runtime type {type_spec!r}",
                error,
            ) from error

    def get_default(self):
        """Return the configured default value."""

        if callable(self._default):
            default_factory = cast(DefaultFactory, self._default)
            return default_factory()
        return self._default

    @property
    def has_default(self):
        """Return whether the field definition has a configured default."""

        return self._default is not UNDEF

    def validate(self, value):
        """Validate and return the final field value."""

        from ._model import Model

        errors = list()
        if self.required and value is UNDEF:
            raise Field.RequiredError("Field is required")
        if value in self.grant:
            return value
        try:
            value = self._validate_runtime_type(value)
        except Exception as error:
            errors.append(("runtime_type", error))

        for function in self._functions:
            try:
                value_ = function(self, value)
                if isinstance(value_, (ListOf, Model)):
                    value = value_
            except Exception as e:
                errors.append((function, e))
        if errors:
            raise Field.VerifyError(errors)
        return value

    @property
    def default(self):
        """Field's default value"""
        return self.get_default()

    @property
    def value(self) -> T:
        """``Field()``'s value
        - Required Field will raise RequiredError if ask for value
          before assigned.
        """

        if self.required and self._value is UNDEF:
            raise Field.RequiredError("Field is required")

        return cast(T, self._value)

    @value.setter
    def value(self, value: T):
        """Set field's value
        - Verify value by field's functions
        - Set fields' value if function return value
        """
        self._value = self.validate(value)

    @overload
    def __get__(self, obj: None, owner: type[Model] | None = None) -> Self: ...

    @overload
    def __get__(self, obj: Model, owner: type[Model] | None = None) -> T: ...

    def __get__(self, obj, owner=None):
        if obj is None:
            return self

        if self._name is None:
            raise AttributeError("Field is not bound to a model attribute")

        bound_field = obj._bound_fields[self._name]
        if self._name not in obj._data and bound_field.has_default is False:
            raise AttributeError(self._name)
        return cast(T, bound_field.value)

    def __set__(self, obj: Model, value: T):
        if self._name is None:
            raise AttributeError("Field is not bound to a model attribute")
        obj[self._name] = value

    def __delete__(self, obj: Model):
        if self._name is None:
            raise AttributeError("Field is not bound to a model attribute")
        del obj[self._name]

    def reset(self):
        """Reset ``Field().value`` to default or ``UNDEF``"""
        self._value = self.get_default()

    def instance(self, type_: type):
        """Verify that ``value`` is instance to ``type_``

        ``assert isinstance(value, type_)``
        """
        self._instance_type = type_
        self._ensure_default_matches_type_spec(type_)
        return self

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
