# Plan

1. Inspect the GitHub Dependabot alerts and identify the affected dependency/version.
2. Update `uv.lock` to use a patched `urllib3` version.
3. Run validation appropriate for a lockfile-only dependency update.
4. Commit and push the fix to `main`.
5. Re-check GitHub Dependabot alert status or note that GitHub may need time to rescan.
