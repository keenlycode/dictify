import sys
from collections import deque
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


def test_ensure_publish_branch_does_nothing_when_local_branch_exists(
    monkeypatch,
) -> None:
    from dev.cli import docs

    calls = []

    def fake_run(command, **kwargs):
        calls.append(command)
        return subprocess_result(0)

    monkeypatch.setattr(docs.subprocess, "run", fake_run)
    monkeypatch.setattr(docs, "run_command", calls.append)

    docs.ensure_publish_branch("docs")

    assert calls == [["git", "rev-parse", "--verify", "--quiet", "docs"]]


def test_ensure_publish_branch_tracks_remote_branch(monkeypatch) -> None:
    from dev.cli import docs

    results = deque([subprocess_result(1), subprocess_result(0)])
    run_calls = []
    command_calls = []

    def fake_run(command, **kwargs):
        run_calls.append(command)
        return results.popleft()

    monkeypatch.setattr(docs.subprocess, "run", fake_run)
    monkeypatch.setattr(docs, "run_command", command_calls.append)

    docs.ensure_publish_branch("docs")

    assert run_calls == [
        ["git", "rev-parse", "--verify", "--quiet", "docs"],
        ["git", "rev-parse", "--verify", "--quiet", "origin/docs"],
    ]
    assert command_calls == [["git", "branch", "--track", "docs", "origin/docs"]]


def test_ensure_publish_branch_does_nothing_without_remote_branch(
    monkeypatch,
) -> None:
    from dev.cli import docs

    results = deque([subprocess_result(1), subprocess_result(1)])
    run_calls = []
    command_calls = []

    def fake_run(command, **kwargs):
        run_calls.append(command)
        return results.popleft()

    monkeypatch.setattr(docs.subprocess, "run", fake_run)
    monkeypatch.setattr(docs, "run_command", command_calls.append)

    docs.ensure_publish_branch("docs")

    assert run_calls == [
        ["git", "rev-parse", "--verify", "--quiet", "docs"],
        ["git", "rev-parse", "--verify", "--quiet", "origin/docs"],
    ]
    assert command_calls == []


def subprocess_result(returncode: int):
    from subprocess import CompletedProcess

    return CompletedProcess(args=[], returncode=returncode)
