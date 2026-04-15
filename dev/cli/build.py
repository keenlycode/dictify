"""Build orchestration commands."""

from __future__ import annotations

from .ai import skill_ref
from .common import run_command
from .docs import docs_build
from .validate import clean_dist, validate_dist


def build() -> None:
    """Build docs, refresh AI skill refs, build, and validate artifacts."""

    clean_dist()
    docs_build()
    skill_ref(check=False)
    run_command(["uv", "build"])
    validate_dist()
