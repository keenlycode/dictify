"""Shared typing aliases used across dictify internals."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from ._field import Field

#: Callable used to validate a field value.
Validator = Callable[..., Any]

#: Callable that returns a fresh default value.
DefaultFactory = Callable[[], Any]

#: Plain string-keyed data mapping used for validated model data.
DataDict = dict[str, Any]

#: Mapping of field names to declared ``Field`` definitions.
if TYPE_CHECKING:
    type FieldMap = dict[str, Field[Any]]
else:
    type FieldMap = dict[str, Any]

#: Mapping of field names to resolved runtime type annotations.
FieldTypeMap = dict[str, Any]

#: Generic field value type.
T = TypeVar("T")
