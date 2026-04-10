"""Build orchestration commands."""

from __future__ import annotations

from .ai import skill_ref
from .common import run_command
from .docs import docs_build


def build() -> None:
    """Build docs, refresh AI skill refs, and build the package."""

    docs_build()
    skill_ref(check=False)
    run_command(["uv", "build"])
