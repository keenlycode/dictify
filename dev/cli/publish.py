"""Publishing commands for the package."""

from __future__ import annotations

from .build import build
from .common import run_command


def publish() -> None:
    """Build fresh artifacts and publish them to PyPI."""

    build()
    run_command(["uv", "publish"])
