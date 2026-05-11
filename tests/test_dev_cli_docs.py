import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_docs_version_line_groups_patch_versions_by_minor_line() -> None:
    from dev.cli.docs import docs_version_line

    assert docs_version_line("4.1.0") == "4.1.x"
    assert docs_version_line("4.1.12") == "4.1.x"


def test_docs_version_line_keeps_existing_labels() -> None:
    from dev.cli.docs import docs_version_line

    assert docs_version_line("4.1.x") == "4.1.x"
    assert docs_version_line("latest") == "latest"
