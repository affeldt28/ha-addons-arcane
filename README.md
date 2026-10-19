# Arcane Community Add-ons for Home Assistant

Two independently installable Edge agents for Home Assistant OS / Supervisor, connecting to an existing Arcane Manager. Choose the access level you need. These are independent community packages and remain experimental until tested on Home Assistant OS.

| Add-on | Docker access | Use it for |
| --- | --- | --- |
| **Arcane Edge Agent (Monitor Only)** | Built-in proxy permits selected inspection requests; Arcane runs as a separate unprivileged user | Container lists, logs, statistics, image/network/volume metadata |
| **Arcane Edge Agent (Full Access — WARNING)** | Direct, unrestricted Docker socket | Deployments, updates, start/stop/restart, deletion, terminal sessions, images, networks and volumes |

> **WARNING — Full Access grants the connected Arcane Manager control over the Docker host, including Home Assistant and Supervisor containers. Operations can break Home Assistant or delete data. Only connect it to a trusted Manager.**

Each add-on includes everything it needs. There is no separate proxy add-on and no repository-specific hostname setup. Both connect outbound and publish no host ports. Each requires Protection mode off because Home Assistant controls Docker socket mounts at the add-on level. Monitor Only runs its internal proxy as root but drops Arcane to UID/GID 65532 and refuses to start if that user can access the real socket. Only the loopback proxy is available to Arcane for Docker requests.

## Install

1. Publish this directory as a public Git repository. Optionally run `python3 tools/configure_repository.py https://github.com/YOUR_ACCOUNT/ha-addons-arcane` to set the repository homepage. No registry publishing is required: Home Assistant builds Monitor Only on the device, while Full Access uses Arcane's official image.
2. Add the public Git URL under **Settings → Apps → Install app → ⋮ → Repositories** (older Home Assistant: **Settings → Add-ons → Add-on Store**).
3. Install the chosen add-on. In Arcane Manager, create an **Edge** environment and copy its generated Manager URL and agent token into the add-on's Configuration tab.
4. Read that add-on's documentation, disable Protection mode and start it. Start on boot is off by default; enable it after confirming the connection.

[Monitor Only setup](arcane_edge_agent/DOCS.md) · [Full Access setup and warning](arcane_edge_agent_full/DOCS.md)

To run both, create a different Arcane environment and token for each. A monitor-only environment does not restrict an independently installed Full Access agent.

## Limits

Full Access has no Docker API method restrictions. Container filesystem, devices, Swarm networking and host bind mounts still depend on the host and Docker configuration. Add-on paths are not necessarily Docker-host paths. Use Home Assistant to manage Supervisor-owned containers and to update these add-ons; replacing the agent through Arcane can conflict with Supervisor. Neither package contains an Arcane Manager web UI.

Monitor Only blocks writes, terminal/exec/attach, container archives and image exports. Arcane can still show action buttons; blocked actions return errors. Metadata and logs may contain secrets. Filtering Docker requests does not make Arcane's own settings/state read-only.

## Development and validation

- `python3 tools/check_policy.py`: check the two add-on definitions and monitoring allowlist.
- `python3 tools/test_proxy.py`: build Monitor Only and test the actual proxy against a fake Docker socket. Includes denial checks for the unprivileged agent user. Requires Docker; never mounts the real host socket.
- CI runs these checks. Live HA OS installation, Arcane pairing, persistence and backup/restore still require testing on a device.

The Monitor Only package version is `2.16.1-2` (Arcane v2.16.1, packaging revision 2); Full Access pulls official `v2.16.1`. Monitor's proxy is pinned to 1.13.1. Update the agent/proxy pins and changelogs when releasing a new version.

[Arcane Edge documentation](https://getarcane.app/docs/remote/environments) · [Arcane socket proxy documentation](https://getarcane.app/docs/security/socket-proxy) · [Home Assistant app configuration](https://contributors.home-assistant.io/apps/reference/configuration/)

## Packaging reference

The [Advanced SSH & Web Terminal add-on, v24.1.7](https://github.com/hassio-addons/app-ssh/tree/v24.1.7) is the packaging reference: one directory per add-on, `rootfs` container files, pinned image inputs, Home Assistant/OCI build labels, user-facing configuration descriptions, and separate README, setup and changelog files.

These Arcane packages remain independent community projects. The monitor uses Docker's init plus its own two-process startup script (`init: true`); it does not use the reference's S6 base, so copying `init: false` would be incorrect. Full Access continues to use the official Arcane image and `legacy: true`. JSON manifests are Home Assistant-supported equivalents of the reference's YAML manifests. Terminal-specific ingress, host networking, hardware access and Supervisor API permissions are not required for either Edge agent.

The optional repository-configuration tool also sets the homepage shown in each add-on's Info tab. English configuration descriptions are supplied under each add-on's `translations` directory. CI checks the monitor startup with ShellCheck as well as the policy and container integration tests.
