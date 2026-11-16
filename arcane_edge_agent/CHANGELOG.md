# Changelog

## 3.0.1-1

- Update Arcane from v2.17.3 to v3.0.1.
- Adopt the Arcane 3 environment variables and default to automatic tunnel transport.
- **Breaking:** polling and legacy enrollment are removed. Upgrade the Manager to Arcane 3, generate a new enrollment token, and configure `ARCANE_MANAGER_API_URL`, `ARCANE_AGENT_TOKEN` and `ARCANE_AGENT_TRANSPORT` before re-enrolling the agent. Back up first and retain the public configuration folder.

## 2.17.1-1

- Align the package version with upstream and add a packaging revision suffix.

## 2.17.2

- Automate image updates and add-on version bumps with Renovate.
- Validate changes before tagging and publishing releases.
- Remove unused build arguments and duplicated image metadata.

Upstream Arcane remains v2.17.1. Package versions are independent of upstream.

See [GitHub Releases](https://github.com/affeldt28/ha-addons-arcane/releases) for subsequent release notes.
