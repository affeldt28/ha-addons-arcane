# Changelog

[Official Arcane changelog](https://github.com/getarcaneapp/arcane/releases) · [Add-on releases](https://github.com/affeldt28/ha-addons-arcane/releases)

## 3.0.1-1

- Update Arcane from v2.17.3 to v3.0.1.
- Adopt the Arcane 3 environment variables and default to automatic tunnel transport.
- **Breaking:** polling and legacy enrollment are removed. Upgrade the Manager to Arcane 3, generate a new enrollment token, and configure `ARCANE_MANAGER_API_URL`, `ARCANE_AGENT_TOKEN` and `ARCANE_AGENT_TRANSPORT` before re-enrolling the agent. Back up first and retain the public configuration folder.

## 2.17.3-1

- Update the upstream Arcane agent from v2.17.1 to v2.17.3.
- Keep both add-on package versions aligned with upstream.

## 2.17.1-1

- Align the package version with upstream and add a packaging revision suffix.

## 2.17.3

- Update the Monitor runtime to Alpine 3.24 and socket-proxy 1.13.2.
- Upstream Arcane remains v2.17.1; this release predates upstream-aligned package versions.

## 2.17.2

- Automate image updates and add-on version bumps with Renovate.
- Validate changes before tagging and publishing releases.
- Remove unused build arguments and duplicated image metadata.

Upstream Arcane remains v2.17.1. At this point, package versions were independent of upstream.
