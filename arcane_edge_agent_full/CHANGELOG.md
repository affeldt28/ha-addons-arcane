# Changelog

## v2.16.2

- Fix Docker connectivity by using Supervisor's `/run/docker.sock` mount directly instead of relying on `/var/run` being a symlink.
- Keep the official `v2.16.1` image tag; this configuration-only fix requires recreating the add-on container with the corrected environment.

## v2.16.1

- Add configuration field descriptions and configurable homepage metadata.
- Add the full official Edge agent with unrestricted Docker access.
- Add prominent warnings in the store name, description and documentation.
- Leave automatic startup disabled by default.
