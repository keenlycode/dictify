# Plan

## Proposed Policy

- Package versions remain exact: `4.1.1`, `4.1.2`, etc.
- Git tags remain exact: `v4.1.1`, `v4.1.2`, etc.
- Docs versions use the minor line: `4.1.x`.
- `latest` points to the latest docs line, currently `4.1.x`.
- Patch releases skip docs publishing unless docs changed or the patch changes documented behavior.

## Implementation Steps

1. Inspect the current deployed docs versions with `mike list` on the docs branch.
2. Update the docs publish workflow so the intended docs version can be a minor-line label like `4.1.x`.
3. Document the policy in the development/release docs so future releases use exact package tags but minor-line docs.
4. Publish `4.1.x` with `latest` after confirmation.
5. Review the version selector and deployed URLs.
6. Decide whether to keep, hide, or delete the old exact `4.1.1` docs entry.

## Open Decision

The main decision is what to do with existing `4.1.1` docs after `4.1.x` is published:

- Keep it visible for now.
- Hide it from the selector but leave the URL alive.
- Delete it after confirming `4.1.x` works.

Recommended: publish `4.1.x` first, verify it, then hide or delete `4.1.1` only if the selector becomes noisy.
