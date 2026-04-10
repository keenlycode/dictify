"""Internal helpers for resolving and validating runtime type specifications."""

from __future__ import annotations

from collections.abc import Mapping
from types import UnionType
from typing import Annotated, Any, get_args, get_origin

from ._sentinel import UNDEF


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

    from ._field import Field

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

    from ._field import ListOf
    from ._model import Model

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
