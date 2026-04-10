"""Root entrypoint for the development CLI."""

from __future__ import annotations

import cyclopts

from . import ai, docs
from .build import build
from .publish import publish

app = cyclopts.App(
    help="Development commands for docs, skills, builds, and publishing."
)
app.command(docs.app, name="docs")
app.command(ai.app, name="ai")
app.command(build)
app.command(publish)


def main() -> None:
    """Run the development CLI."""

    app()


if __name__ == "__main__":
    main()
