# AGENTS.md

Use the `automata-agent` guidance when changing repository agent behavior, agent configuration, delegation policy, or durable agent workspace conventions.

This repository uses `.agents/` as its agent workspace.

- `.agents/skills/`: repository-local skills
- `.agents/tasks/`: durable task state for multi-step work
- `.codex/agents/`: Codex runtime agent definitions

For multi-step work, create or resume task state under `.agents/tasks/` before implementation. Treat the task files there as the source of truth for plan, progress, actions, and artifacts.
