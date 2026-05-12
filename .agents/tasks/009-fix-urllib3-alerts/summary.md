# Fix urllib3 Dependabot Alerts

Goal: resolve open GitHub Dependabot alerts for transitive `urllib3` vulnerabilities in `uv.lock`.

Scope:
- Inspect open GitHub Dependabot alerts.
- Update the affected locked dependency to a patched version.
- Validate the repository after the dependency update.
- Commit and push the fix if validation passes.

Constraints:
- Keep package release metadata unchanged unless required.
- Prefer repository-local validation commands from `dev/cli`.

Owner: primary project agent.
