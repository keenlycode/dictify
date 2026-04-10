"""dictify provides lightweight schema and validation helpers for dict data."""

from ._field import Field, ListOf
from ._model import Model
from ._sentinel import UNDEF

__all__ = ["UNDEF", "Field", "ListOf", "Model"]
