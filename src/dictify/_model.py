"""Model implementation and per-instance bound field state for dictify."""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from typing import Any, get_type_hints

from ._field import Field, ListOf
from ._sentinel import UNDEF
from ._types import FieldMap, FieldTypeMap
from ._utils import _normalize_simple_type_spec, _resolve_field_annotation


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
