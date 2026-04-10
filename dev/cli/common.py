"""Shared helpers for repository development commands."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run_command(command: list[str]) -> None:
    """Run a command in the repository root and fail on error."""

    subprocess.run(command, cwd=ROOT, check=True)
