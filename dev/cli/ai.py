"""AI skill generation commands."""

from __future__ import annotations

from pathlib import Path

import cyclopts

from .common import ROOT

app = cyclopts.App(help="Generate packaged AI skill assets.")

DOCS_DIR = ROOT / "docs-src"
GUIDE_DIR = DOCS_DIR / "guide"
SKILL_DIR = ROOT / "src" / "dictify" / "ai_skills" / "dictify-usage"
REFERENCES_DIR = SKILL_DIR / "references"
GENERATED_HEADER = "<!-- Generated from script, do not edit directly. -->\n\n"


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
    body = body.replace("(guide/usage/index.md)", "(usage/index.md)")
    body = body.replace("(guide/field-api/index.md)", "(field-api/index.md)")
    body = body.replace(
        "(guide/validation-recipes/index.md)", "(validation-recipes/index.md)"
    )
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


def remove_stale_references(expected: set[Path], check: bool) -> bool:
    """Remove generated reference files that no longer have source docs."""

    ok = True
    for path in sorted(REFERENCES_DIR.rglob("*.md")):
        if path in expected:
            continue
        if not path.read_text(encoding="utf-8").startswith(GENERATED_HEADER):
            continue
        if check:
            print(f"stale: {path.relative_to(ROOT)}")
            ok = False
            continue
        path.unlink()
        print(f"removed: {path.relative_to(ROOT)}")
    return ok


@app.command(name="skill-ref")
def skill_ref(*, check: bool = False) -> None:
    """Sync packaged Dictify skill references from docs-src."""

    ok = True
    expected = {REFERENCES_DIR / "index.md"}
    for source in sorted(GUIDE_DIR.rglob("*.md")):
        target = REFERENCES_DIR / source.relative_to(GUIDE_DIR)
        expected.add(target)
        ok &= sync_file(target, build_reference(source), check)

    ok &= sync_file(REFERENCES_DIR / "index.md", build_index_reference(), check)
    ok &= remove_stale_references(expected, check)
    if not ok:
        raise SystemExit(1)
