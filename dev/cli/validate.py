"""Distribution validation commands for package releases."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

from .common import ROOT, run_command

DIST_DIR = ROOT / "dist"


def clean_dist() -> None:
    """Remove existing build artifacts so release builds start clean."""

    shutil.rmtree(DIST_DIR, ignore_errors=True)


def validate_dist() -> None:
    """Run metadata and install smoke checks against built artifacts."""

    artifacts = sorted(DIST_DIR.glob("*.whl")) + sorted(DIST_DIR.glob("*.tar.gz"))
    if not artifacts:
        raise FileNotFoundError("No build artifacts found in dist/")

    run_command(["uv", "run", "--group", "dev", "twine", "check", *map(str, artifacts)])

    for artifact in artifacts:
        _smoke_test_artifact(artifact)


def _smoke_test_artifact(artifact: Path) -> None:
    """Install an artifact into an isolated venv and verify basics."""

    with tempfile.TemporaryDirectory(prefix="dictify-release-") as temp_dir:
        env_dir = Path(temp_dir) / "venv"
        venv.EnvBuilder(with_pip=True).create(env_dir)
        python = env_dir / "bin" / "python"
        command = [
            str(python),
            "-m",
            "pip",
            "install",
            str(artifact),
        ]
        subprocess.run(command, cwd=ROOT, check=True)

        subprocess.run(
            [str(python), "-c", "import dictify; print(dictify.__all__)"],
            cwd=ROOT,
            check=True,
        )
        subprocess.run(
            [str(python), "-m", "dictify.cli.dictify", "--help"], cwd=ROOT, check=True
        )
        subprocess.run(
            [
                str(python),
                "-c",
                (
                    "from importlib.resources import files; "
                    "root = files('dictify').joinpath('ai_skills'); "
                    "skill = root.joinpath('dictify-usage'); "
                    "assert skill.joinpath('SKILL.md').is_file(); "
                    "refs = skill.joinpath('references'); "
                    "assert refs.joinpath('field-api.md').is_file(); "
                    "assert refs.joinpath('usage', 'index.md').is_file()"
                ),
            ],
            cwd=ROOT,
            check=True,
        )


def release_check() -> None:
    """Build and validate release artifacts from a clean tree."""

    clean_dist()
    run_command([sys.executable, "-m", "dev.cli", "ai", "skill-ref", "--check"])
    run_command(["uv", "run", "pytest", "tests/test_dictify.py"])
    run_command(["uv", "run", "ruff", "check", "src", "tests", "dev"])
    run_command(["uv", "run", "ty", "check"])
    run_command(["uv", "run", "--group", "docs", "mkdocs", "build"])
    run_command(["uv", "build"])
    validate_dist()
