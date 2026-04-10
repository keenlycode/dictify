"""Docs-related development commands."""

from __future__ import annotations

import cyclopts

from .common import run_command

app = cyclopts.App(help="Build or serve the documentation site.")


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
    """Publish versioned docs with mike and update the default alias."""

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
            version,
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
