"""dictify provides lightweight schema and validation helpers for dict data."""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping, MutableMapping
from functools import wraps
from types import UnionType
from typing import (
    Annotated,
    Any,
    Self,
    TypeVar,
    cast,
    get_args,
    get_origin,
    get_type_hints,
    overload,
)

Validator = Callable[..., Any]
DefaultFactory = Callable[[], Any]
DataDict = dict[str, Any]
FieldMap = dict[str, "Field[Any]"]
FieldTypeMap = dict[str, Any]
T = TypeVar("T")


def _strip_annotated_type(type_spec: Any):
    """Return the underlying type from an Annotated declaration."""

    while get_origin(type_spec) is Annotated:
        type_spec = get_args(type_spec)[0]
    return type_spec


def _resolve_field_annotation(annotation: Any):
    """Return the runtime type for a field annotation.

    Annotated metadata is ignored for runtime typing, except that Field metadata
    is rejected to avoid ambiguous double-field declarations.
    """

    while get_origin(annotation) is Annotated:
        base, *metadata = get_args(annotation)
        if any(isinstance(item, Field) for item in metadata):
            raise Field.DefineError(
                "Field metadata inside Annotated[...] is ambiguous when the "
                "class attribute is also assigned to Field(...)"
            )
        annotation = base
    return annotation


def _normalize_simple_type_spec(type_spec: Any):
    """Return comparable runtime types for plain types, tuples, and unions."""

    type_spec = _strip_annotated_type(type_spec)

    if isinstance(type_spec, tuple):
        if all(isinstance(item, type) for item in type_spec):
            return frozenset(type_spec)
        return None

    origin = get_origin(type_spec)
    if origin is UnionType:
        normalized = []
        for arg in get_args(type_spec):
            if not isinstance(arg, type):
                return None
            normalized.append(arg)
        return frozenset(normalized)

    if isinstance(type_spec, type):
        return frozenset([type_spec])

    return None


def _validate_type_spec(value, type_spec):
    """Validate a value against a runtime type specification."""

    type_spec = _strip_annotated_type(type_spec)

    if type_spec in (UNDEF, Any):
        return value

    origin = get_origin(type_spec)
    if origin is UnionType:
        errors = []
        for option in get_args(type_spec):
            try:
                return _validate_type_spec(value, option)
            except Exception as error:
                errors.append(error)
        raise AssertionError(errors)

    if origin is list:
        assert isinstance(value, list), f"{type(value)} is not instance of {list}"
        item_types = get_args(type_spec)
        if not item_types:
            return ListOf(value)
        return ListOf([_validate_type_spec(item, item_types[0]) for item in value])

    if isinstance(type_spec, tuple):
        model_types = tuple(
            type_
            for type_ in type_spec
            if isinstance(type_, type) and issubclass(type_, Model)
        )
        if isinstance(value, Mapping):
            for model_cls in model_types:
                try:
                    return model_cls(value)
                except Exception:
                    pass
        assert isinstance(value, type_spec), (
            f"{type(value)} is not instance of {type_spec}"
        )
        return value

    if isinstance(type_spec, type) and issubclass(type_spec, Model):
        if isinstance(value, Mapping):
            return type_spec(value)
        assert isinstance(value, type_spec), (
            f"{type(value)} is not instance of {type_spec}"
        )
        return value

    if isinstance(type_spec, type):
        assert isinstance(value, type_spec), (
            f"{type(value)} is not instance of {type_spec}"
        )
        return value

    return value


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
    __field_types__: FieldTypeMap = {}

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
        field_types = {}
        type_hints = get_type_hints(cls, include_extras=True)
        for base in reversed(cls.__mro__[1:]):
            fields.update(getattr(base, "__fields__", {}))
            field_types.update(getattr(base, "__field_types__", {}))
        for key, value in vars(cls).items():
            if isinstance(value, Field):
                value._name = key
                fields[key] = value
                if key in type_hints:
                    annotation = _resolve_field_annotation(type_hints[key])
                    field_types[key] = annotation
                    normalized_annotation = _normalize_simple_type_spec(annotation)
                    normalized_instance = _normalize_simple_type_spec(
                        value._instance_type
                    )
                    if (
                        normalized_annotation is not None
                        and normalized_instance is not None
                        and normalized_annotation != normalized_instance
                    ):
                        raise Field.DefineError(
                            f"{cls.__name__}.{key}: annotation {annotation!r} "
                            f"conflicts with instance({value._instance_type!r})"
                        )
                    value._annotation_type = annotation
                    if value._instance_type is UNDEF:
                        value._ensure_default_matches_type_spec(annotation)
        cls.__fields__ = fields
        cls.__field_types__ = field_types

    def __init__(self, data: Mapping[str, Any] | None = None, strict: bool = True):
        """Create a model instance from mapping data and validate declared fields."""

        if data is None:
            data = {}
        assert isinstance(data, Mapping), (
            "Model initial data should be instance of mapping"
        )
        assert isinstance(strict, bool)
        data = dict(data)
        object.__setattr__(
            self,
            "_bound_fields",
            {
                key: BoundField(field)
                for key, field in self.__class__.__fields__.items()
            },
        )
        object.__setattr__(self, "_data", {})
        object.__setattr__(self, "_strict", strict)

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

    def __getattr__(self, key):
        """Expose non-field extras as attributes when they exist in model data."""

        if key.startswith("_"):
            raise AttributeError(key)

        data = self.__dict__.get("_data")
        if data is not None and key not in self.__class__.__fields__ and key in data:
            return data[key]
        raise AttributeError(key)

    def __setattr__(self, key, value):
        """Route public attribute writes through field or strict model semantics."""

        if key.startswith("_") or "_data" not in self.__dict__:
            object.__setattr__(self, key, value)
            return

        if key in self.__class__.__fields__:
            self[key] = value
            return

        if self._strict is False:
            self[key] = value
            return

        raise AttributeError(key)

    def __delattr__(self, key):
        """Route public attribute deletes through field or strict model semantics."""

        if key.startswith("_") or "_data" not in self.__dict__:
            object.__delattr__(self, key)
            return

        if key in self.__class__.__fields__:
            del self[key]
            return

        if self._strict is False and key in self._data:
            del self[key]
            return

        raise AttributeError(key)

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
