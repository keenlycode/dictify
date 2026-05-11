# Fix Dependabot Alerts

## Goal

Resolve the five high Dependabot alerts reported by GitHub for the Dictify default branch.

## Scope

- Inspect the actual GitHub Dependabot alert details.
- Update only the affected dependency constraints or lockfile entries where practical.
- Run the repository validation gate needed for confidence.
- Commit the fix if repository files change.

## Constraints

- Do not guess vulnerable packages from the push warning alone.
- Do not publish a new package release unless runtime package metadata changes and the user confirms the release.
- Keep release/docs publishing separate from this security maintenance unless required.

## References

- GitHub Dependabot page: https://github.com/keenlycode/dictify/security/dependabot
- Release gate: `uv run python -m dev.cli release-check`
