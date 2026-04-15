# AI Skill

## Installed CLI

`dictify` includes an installed CLI for the packaged AI skill.

```shell
dictify ai-skill-install
```

The command prompts for the exact destination folder and defaults to:

```text
./.agents/skills/dictify-usage
```

If the destination already exists, `dictify` asks before overwriting it.

The installed skill contains:

- `SKILL.md`
- `agents/openai.yaml`
- generated markdown references copied from `docs-src/`
