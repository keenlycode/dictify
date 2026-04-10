"""AI skill generation commands."""

from __future__ import annotations

from pathlib import Path

import cyclopts

from .common import ROOT

app = cyclopts.App(help="Generate packaged AI skill assets.")

DOCS_DIR = ROOT / "docs-src"
SKILL_DIR = ROOT / "src" / "dictify" / "ai_skills" / "dictify-usage"
REFERENCES_DIR = SKILL_DIR / "references"
GENERATED_HEADER = "<!-- Generated from script, do not edit directly. -->\n\n"

SOURCE_MAP = {
    DOCS_DIR / "guide" / "usage.md": REFERENCES_DIR / "usage.md",
    DOCS_DIR / "guide" / "field-api.md": REFERENCES_DIR / "field-api.md",
    DOCS_DIR / "guide" / "validation-recipes.md": REFERENCES_DIR
    / "validation-recipes.md",
}


def load_text(path: Path) -> str:
    """Return UTF-8 text for an existing file."""

    return path.read_text(encoding="utf-8")


def remove_home_hero(text: str) -> str:
    """Strip the docs homepage hero HTML block for AI-focused references."""

    lines = text.splitlines()
    if not lines or lines[0].strip() != '<section class="home-hero">':
        return text.strip() + "\n"

    try:
        end_index = lines.index("</section>")
    except ValueError:
        return text.strip() + "\n"

    trimmed = "\n".join(lines[end_index + 1 :]).strip()
    return trimmed + "\n"


def build_index_reference() -> str:
    """Return the generated index reference content."""

    source = load_text(DOCS_DIR / "index.md")
    body = remove_home_hero(source)
    body = body.replace("(guide/usage.md)", "(usage.md)")
    body = body.replace("(guide/field-api.md)", "(field-api.md)")
    body = body.replace("(guide/validation-recipes.md)", "(validation-recipes.md)")
    return GENERATED_HEADER + body


def build_reference(source: Path) -> str:
    """Return generated content for a copied markdown reference."""

    return GENERATED_HEADER + load_text(source).strip() + "\n"


def ensure_parent(path: Path) -> None:
    """Create the parent directory for a generated file."""

    path.parent.mkdir(parents=True, exist_ok=True)


def sync_file(path: Path, content: str, check: bool) -> bool:
    """Write a generated file or report whether it is current."""

    current = path.read_text(encoding="utf-8") if path.exists() else None
    if current == content:
        return True

    if check:
        print(f"out of date: {path.relative_to(ROOT)}")
        return False

    ensure_parent(path)
    path.write_text(content, encoding="utf-8")
    print(f"updated: {path.relative_to(ROOT)}")
    return True


@app.command(name="skill-ref")
def skill_ref(*, check: bool = False) -> None:
    """Sync packaged Dictify skill references from docs-src."""

    ok = True
    for source, destination in SOURCE_MAP.items():
        if not source.exists():
            raise FileNotFoundError(source)
        ok &= sync_file(destination, build_reference(source), check)

    ok &= sync_file(REFERENCES_DIR / "index.md", build_index_reference(), check)
    if not ok:
        raise SystemExit(1)
