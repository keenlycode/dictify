"""Installed Dictify CLI commands."""

from __future__ import annotations

import shutil
from importlib.resources import as_file, files
from pathlib import Path

import cyclopts

app = cyclopts.App(help="Dictify command-line tools.")

DEFAULT_SKILL_DESTINATION = Path("./.agents/skills/dictify-usage")


def _prompt_destination() -> Path:
    """Prompt for the exact skill installation destination."""

    prompt = f"Install Dictify skill to [{DEFAULT_SKILL_DESTINATION}]: "
    response = input(prompt).strip()
    if not response:
        return DEFAULT_SKILL_DESTINATION
    return Path(response).expanduser()


def _confirm_overwrite(path: Path) -> bool:
    """Return whether an existing destination may be overwritten."""

    response = input("Destination exists. Overwrite? [y/N]: ").strip().lower()
    return response in {"y", "yes"}


@app.command(name="ai-skill-install")
def ai_skill_install() -> None:
    """Interactively install the packaged Dictify AI skill."""

    destination = _prompt_destination()
    skill_resource = files("dictify").joinpath("ai_skills").joinpath("dictify-usage")

    with as_file(skill_resource) as source:
        if destination.exists():
            if not _confirm_overwrite(destination):
                print("Cancelled.")
                return
            if destination.is_dir():
                shutil.rmtree(destination)
            else:
                destination.unlink()

        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, destination)

    print(f"Installed Dictify skill to {destination}")


def main() -> None:
    """Run the installed Dictify CLI."""

    app()
