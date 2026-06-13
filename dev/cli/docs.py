"""Docs-related development commands."""

from __future__ import annotations

import re
import subprocess

import cyclopts

from .common import ROOT, run_command

app = cyclopts.App(help="Build or serve the documentation site.")

PATCH_VERSION_RE = re.compile(
    r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)$"
)


def docs_version_line(version: str) -> str:
    """Return the docs version label for a package version."""

    match = PATCH_VERSION_RE.fullmatch(version)
    if match is None:
        return version
    return f"{match.group('major')}.{match.group('minor')}.x"


def ensure_publish_branch(branch: str) -> None:
    """Create a local tracking branch when only ``origin/<branch>`` exists."""

    local = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", branch],
        cwd=ROOT,
        check=False,
        stdout=subprocess.DEVNULL,
    )
    if local.returncode == 0:
        return

    remote = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"origin/{branch}"],
        cwd=ROOT,
        check=False,
        stdout=subprocess.DEVNULL,
    )
    if remote.returncode != 0:
        return

    run_command(["git", "branch", "--track", branch, f"origin/{branch}"])


@app.command(name="build")
def docs_build() -> None:
    """Build the docs site with MkDocs."""

    run_command(["uv", "run", "--group", "docs", "mkdocs", "build"])


@app.command(name="dev")
def docs_dev(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Run the MkDocs live-reload development server."""

    run_command(
        [
            "uv",
            "run",
            "--group",
            "docs",
            "mkdocs",
            "serve",
            "-a",
            f"{host}:{port}",
        ]
    )


@app.command(name="publish")
def docs_publish(version: str, alias: str = "latest", branch: str = "docs") -> None:
    """Publish minor-line docs with mike and update the default alias."""

    docs_version = docs_version_line(version)
    ensure_publish_branch(branch)

    run_command(
        [
            "uv",
            "run",
            "--group",
            "docs",
            "mike",
            "deploy",
            "--push",
            "--branch",
            branch,
            "--update-aliases",
            docs_version,
            alias,
        ]
    )
    run_command(
        [
            "uv",
            "run",
            "--group",
            "docs",
            "mike",
            "set-default",
            "--push",
            "--branch",
            branch,
            alias,
        ]
    )
