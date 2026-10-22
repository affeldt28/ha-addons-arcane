# Full Access setup

> **WARNING: unrestricted Docker control. The connected Manager can change or delete containers, images, networks and volumes, including resources used by Home Assistant. This can stop Home Assistant or cause data loss. Only connect to a Manager you trust.**

1. Install **Arcane Agent (Full Access)** only if you intend to grant host Docker control.
2. In your separate Arcane Manager, create an Edge environment. If you also run Monitor Only, use a different environment and token.
3. Set `MANAGER_API_URL`, `AGENT_TOKEN` and `EDGE_TRANSPORT` in Configuration. Poll is the default; auto, websocket and grpc are also available. Use HTTPS for remote connections.
4. Disable Protection mode to permit Docker socket access. Start the add-on and confirm it connects. Start on boot is off by default; enable it after testing.

## Features and host limits

This package builds locally from the official Arcane agent binary, pinned independently of the add-on package version. It runs as root with `DOCKER_HOST=unix:///run/docker.sock`. There is no method/path proxy. Container deployment, start/stop/restart, deletion, exec/terminal, image management, networks and volumes are available through the agent, subject to your Arcane user permissions and Docker host capabilities.

Host filesystem browsing, arbitrary Compose bind mounts, hardware access, GPU support and Swarm networking depend on the host configuration. This package does not mount the host root or Docker volume directory into the agent. Docker resolves bind source paths on the host, not relative to the agent container. Direct Docker access can itself create containers with additional host mounts or privileges.

Supervisor owns Home Assistant and its add-on containers. Use Home Assistant for their lifecycle and updates. Arcane agent self-update and automatic pruning/updating of Supervisor-managed resources may conflict with Supervisor. The package intentionally adds no Supervisor API permissions, exposed host ports or blanket hardware access; Docker access already grants substantial host control.

This is an Edge agent, not the Arcane Manager web application.

## Persistence and troubleshooting

State is stored in `/config/arcane` inside the container, linked to `/app/data`. Pairing settings are saved in `/config/options.json` with owner-only permissions. Supervisor exposes this public folder under `/addon_configs/<repository>_<slug>` (some newer tools call it `/app_configs`). It is included in cold add-on backups.

On first start after updating, existing private state is copied automatically; retained public state is never overwritten. **Update and start the add-on before uninstalling** so migration can run. When uninstalling, leave the option to remove the public configuration folder unchecked. Reinstall from the same repository with the same slug to reuse the folder. Deleting that folder also deletes the retained state.

After reinstall, leave Manager URL and token blank to reuse saved pairing settings, including transport. To replace them, enter both fields in the Configuration tab; valid settings are saved at startup. Home Assistant's Configuration form itself is not restored from this file. Backups and the public folder contain credentials; protect them accordingly. Restart after changing options.

Storage follows [Home Assistant's public configuration folder guidance](https://contributors.home-assistant.io/blog/2023/11/06/public-addon-config/) and [configuration file lifecycle](https://contributors.home-assistant.io/apps/guides/options/#configuration-files-for-users).


For Docker permission errors, verify Protection mode is off. Supervisor mounts the Docker socket at `/run/docker.sock`; the agent must use `DOCKER_HOST=unix:///run/docker.sock`. A `no such file or directory` error mentioning `/var/run/docker.sock` indicates the old configuration. After installing the corrected package, stop and start the add-on so Supervisor recreates its container with the updated environment. For pairing failures, check Manager URL, token, TLS and outbound connectivity. Polling Standby is healthy.
