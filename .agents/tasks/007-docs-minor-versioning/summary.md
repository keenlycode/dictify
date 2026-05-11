# Docs Minor Versioning

## Goal

Group published documentation by minor release line, such as `4.1.x`, instead of publishing a separate docs version for every patch release.

## Scope

- Define the docs versioning policy for Dictify patch releases.
- Decide how `latest` and older exact patch docs, such as `4.1.1`, should behave.
- Identify required changes to the docs publishing workflow and documentation.

## Constraints

- Do not publish docs until explicitly confirmed.
- Do not change package versions or release tags for this docs policy alone.
- Prefer repository-local commands from `dev/cli`.
- Keep existing public docs URLs in mind before deleting or hiding versions.

## Expected Outcome

A clear implementation plan for publishing docs as `4.1.x` while keeping package releases and git tags exact.
