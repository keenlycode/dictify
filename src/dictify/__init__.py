"""dictify provides lightweight schema and validation helpers for dict data."""

from __future__ import annotations

import re
from collections.abc import Mapping, MutableMapping
from functools import wraps
from typing import Any, Callable, cast

Validator = Callable[..., Any]
DefaultFactory = Callable[[], Any]
DataDict = dict[str, Any]
FieldMap = dict[str, "Field"]


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


class _UNDEF:
    """Sentinel type used to represent an unset value."""

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
        if self.types[0] is UNDEF:
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

        errors = list()
        if self.required and value is UNDEF:
            raise Field.RequiredError("Field is required")
        if value in self.grant:
            return value

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
    def value(self):
        """``Field()``'s value
        - Required Field will raise RequiredError if ask for value
          before assigned.
        """

        if self.required and self._value is UNDEF:
            raise Field.RequiredError("Field is required")

        return self._value

    @value.setter
    def value(self, value):
        """Set field's value
        - Verify value by field's functions
        - Set fields' value if function return value
        """
        self._value = self.validate(value)

    def reset(self):
        """Reset ``Field().value`` to default or ``UNDEF``"""
        self._value = self.get_default()

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


class BoundField:
    """Runtime field state for a single model instance.

    Model class attributes like ``User.email = Field(...)`` are created once at
    class definition time and reused as shared schema definitions. BoundField
    keeps the per-instance value separate so model instances do not share Field
    runtime state.
    """

    def __init__(self, definition: Field):
        self.definition = definition
        self._value = self.definition.get_default()

    @property
    def has_default(self):
        """Return whether the field definition has a configured default."""

        return self.definition.has_default

    @property
    def default(self):
        """Return a fresh default value from the wrapped field definition."""

        return self.definition.get_default()

    @property
    def value(self):
        """Return the current bound value, enforcing required-field access."""

        if self.definition.required and self._value is UNDEF:
            raise Field.RequiredError("Field is required")
        return self._value

    @value.setter
    def value(self, value):
        self._value = self.definition.validate(value)

    def reset(self):
        """Reset the bound value back to the field definition default."""

        self._value = self.default


class Model(MutableMapping[str, Any]):
    """Modified mapping that can define ``Field`` in it's class."""

    # Class-level schema collected once from Field declarations.
    __fields__: FieldMap = {}

    class Error(Exception):
        """``Exception`` when data doesn't pass ``Model`` validation."""

        pass

    def __init_subclass__(cls, **kwargs):
        """Collect class-declared Field definitions into ``cls.__fields__``.

        ``Field(...)`` expressions in a Model class body run once when the
        subclass is defined, so those objects act as shared schema templates.
        Per-instance runtime values are stored separately in BoundField objects.
        """

        super().__init_subclass__(**kwargs)
        fields = {}
        for base in reversed(cls.__mro__[1:]):
            fields.update(getattr(base, "__fields__", {}))
        for key, value in vars(cls).items():
            if isinstance(value, Field):
                fields[key] = value
        cls.__fields__ = fields

    def __init__(self, data: Mapping[str, Any] | None = None, strict: bool = True):
        """Create a model instance from mapping data and validate declared fields."""

        if data is None:
            data = {}
        assert isinstance(data, Mapping), (
            "Model initial data should be instance of mapping"
        )
        assert isinstance(strict, bool)
        data = dict(data)
        self._bound_fields = {
            key: BoundField(field) for key, field in self.__class__.__fields__.items()
        }
        self._data: DataDict = {}
        self._strict = strict

        errors = {}
        for key, field in self.__class__.__fields__.items():
            bound_field = self._bound_fields[key]
            if key in data:
                continue
            if bound_field.has_default:
                self._data[key] = bound_field.value
            elif field.required:
                errors[key] = Field.RequiredError("This field is required")
        if errors:
            raise Model.Error(errors)

        self._commit_validated(self._validate_mapping(data))
        self.post_validate()

    def __getitem__(self, key):
        """Return a validated stored value by key."""

        return self._data[key]

    def __iter__(self):
        """Iterate over stored model keys."""

        return iter(self._data)

    def __len__(self):
        """Return the number of stored keys."""

        return len(self._data)

    def __eq__(self, other):
        """Compare model data against another mapping by value."""

        if isinstance(other, Mapping):
            return dict(self) == dict(other)
        return NotImplemented

    def _validate_item(self, key, value):
        """Validate one key/value pair against the declared schema."""

        if key not in self.__class__.__fields__:
            if self._strict is False:
                return value
            raise KeyError("Field is not defined")
        return self._bound_fields[key].definition.validate(value)

    def _validate_mapping(self, data: Mapping[str, Any]):
        """Validate a mapping and return validated values or raise Model.Error."""

        errors = {}
        validated = {}
        for key, value in data.items():
            try:
                validated[key] = self._validate_item(key, value)
            except (Field.VerifyError, KeyError) as error:
                errors[key] = error
        if errors:
            raise Model.Error(errors)
        return validated

    def _commit_validated(self, data: Mapping[str, Any]):
        """Persist validated values into bound fields and model storage."""

        for key, value in data.items():
            if key in self.__class__.__fields__:
                self._bound_fields[key]._value = value
            self._data[key] = value

    def __delitem__(self, key):
        """Delete item but also check for Field's default or required option."""

        if (key not in self.__class__.__fields__) and (self._strict is False):
            del self._data[key]
            self.post_validate()
            return

        bound_field = self._bound_fields[key]
        if bound_field.has_default:
            bound_field.reset()
            self._data[key] = bound_field.value
        elif bound_field.definition.required:
            raise Model.Error({key: Field.RequiredError("Field is required")})
        else:
            del self._data[key]
            bound_field._value = UNDEF
        self.post_validate()

    def __setitem__(self, key, value):
        """Set ``value`` if is valid."""

        try:
            validated = self._validate_item(key, value)
        except (Field.VerifyError, KeyError) as error:
            raise Model.Error({key: error}) from error

        self._commit_validated({key: validated})
        self.post_validate()

    def pop(self, *args, **kw):
        """Unsupported because schema-aware delete semantics are not defined."""

        raise NotImplementedError

    def popitem(self, *args, **kw):
        """Unsupported because schema-aware delete semantics are not defined."""

        raise NotImplementedError

    def clear(self):
        """Unsupported because clearing may violate required/default field rules."""

        raise NotImplementedError

    def post_validate(self):
        """Hook for cross-field validation after successful model mutations."""

        pass

    def setdefault(self, key, default=None):
        """Return an existing value or validate and store the provided default."""

        if key in self:
            return self[key]
        self[key] = default
        return self[key]

    def update(self, data=None, **kwargs):
        """Update ``data`` if is valid."""
        if data is None:
            data = {}
        validated = self._validate_mapping(dict(data, **kwargs))
        self._commit_validated(validated)
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
