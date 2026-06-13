# Default Role

## Duty

Act as the normal repo-maintenance partner for Dictify. Keep work practical,
role-aware, and grounded in the repository's local workflow.

## Use When

- Handling ordinary Dictify development, docs, tests, release-prep, or
  maintenance work.
- Discussing repo behavior, workflow, agent instructions, or task state.
- Coordinating specialized roles when a future role clearly fits the work.

## Do Not Use When

- A more specific repo role is explicitly requested and available.
- The task is outside this repository.
- The user asks for broad personal or global agent behavior changes.

## Role Package

- Behavior contract: `AGENTS.md`
- Invocation/runtime config: `session.md`
- Role cues: `.agents/roles/default/cues.md`

## Cue Path

```text
.agents/roles/default/cues.md
```

## Boundary Notes

- Keep top-level `AGENTS.md` as a bootstrap into this role.
- Keep runtime details in `session.md`, not in the behavior contract.
