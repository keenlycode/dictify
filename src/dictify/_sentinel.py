"""Sentinel values shared across dictify internals."""

from __future__ import annotations


class _UNDEF:
    """Sentinel type used to represent an unset value."""

    def __repr__(self):
        return "UNDEF"


UNDEF = _UNDEF()
