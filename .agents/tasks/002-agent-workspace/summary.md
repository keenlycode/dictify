# Agent Workspace Convention

## Goal

Move durable agent task state into `.agents/tasks/` and document `.agents/` as the repository agent workspace.

## Scope

- Add repo-level `AGENTS.md` guidance for agent workspace conventions.
- Update Codex default-agent behavior to use `.agents/tasks/`.
- Add a short Dictify development skill reminder for multi-step work.
- Preserve existing task history by migrating it from `tasks/` to `.agents/tasks/`.

## Expected Outcome

Future agents use `.agents/tasks/` as the durable source of truth for task plans, progress, actions, and artifacts.
