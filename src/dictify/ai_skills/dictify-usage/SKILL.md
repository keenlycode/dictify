---
name: dictify-usage
description: Use Dictify correctly for standalone field validation and annotation-first mapping models. Use when writing code or examples that should validate Python mappings or JSON-like documents with `Field`, `Model`, `ListOf`, or `UNDEF`.
---

# Dictify Usage

Use Dictify from an installed Python environment.

## Workflow

1. Read the relevant files under `references/`.
2. Use the installed public API: `from dictify import Field, Model, ListOf, UNDEF`.
3. If the references are not enough, inspect the installed `dictify` package implementation in the active Python environment.

Prefer `Annotated[..., Field(...)]` for new model declarations. Direct assignment declarations remain supported when matching existing code.
