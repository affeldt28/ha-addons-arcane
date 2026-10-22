# Changelog

## 2.16.1-1

- Fix Docker connectivity by using Supervisor's `/run/docker.sock` mount directly instead of relying on `/var/run` being a symlink.
- Build the package locally with upstream Arcane pinned to `v2.16.1`, allowing independent package releases.
- Move agent state and saved pairing settings to the public add-on config folder, with automatic migration from private storage. Keep that folder when uninstalling to reuse it after reinstall.

## v2.16.1

- Add configuration field descriptions and configurable homepage metadata.
- Add the full official Edge agent with unrestricted Docker access.
- Add prominent warnings in the store name, description and documentation.
- Leave automatic startup disabled by default.
