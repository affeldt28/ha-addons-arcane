# Full Access setup

> **WARNING: unrestricted Docker control. The connected Manager can change or delete containers, images, networks and volumes, including resources used by Home Assistant. This can stop Home Assistant or cause data loss. Only connect to a Manager you trust.**

1. Install **Arcane Agent (Full Access)** only if you intend to grant host Docker control.
2. In your separate Arcane Manager, create an Edge environment. If you also run Monitor Only, use a different environment and token.
3. Set `MANAGER_API_URL`, `AGENT_TOKEN` and `EDGE_TRANSPORT` in Configuration. Poll is the default; auto, websocket and grpc are also available. Use HTTPS for remote connections.
4. Disable Protection mode to permit Docker socket access. Start the add-on and confirm it connects. Start on boot is off by default; enable it after testing.

## Features and host limits

This package uses the pinned official Arcane agent image unchanged, adding only Home Assistant image labels. Supervisor passes Configuration fields directly as environment variables (`legacy: true`); there is no custom startup script. It runs as root with `DOCKER_HOST=unix:///run/docker.sock`. There is no method/path proxy. Container deployment, start/stop/restart, deletion, exec/terminal, image management, networks and volumes are available through the agent, subject to your Arcane user permissions and Docker host capabilities.

Host filesystem browsing, arbitrary Compose bind mounts, hardware access, GPU support and Swarm networking depend on the host configuration. This package does not mount the host root or Docker volume directory into the agent. Docker resolves bind source paths on the host, not relative to the agent container. Direct Docker access can itself create containers with additional host mounts or privileges.

Supervisor owns Home Assistant and its add-on containers. Use Home Assistant for their lifecycle and updates. Arcane agent self-update and automatic pruning/updating of Supervisor-managed resources may conflict with Supervisor. The package intentionally adds no Supervisor API permissions, exposed host ports or blanket hardware access; Docker access already grants substantial host control.

This is an Edge agent, not the Arcane Manager web application.

## Persistence and troubleshooting

The public add-on configuration folder is mounted directly at the official image's `/app/data` path and included in cold add-on backups. Keep this folder when uninstalling if you want to retain agent state. Pairing settings come from Home Assistant's Configuration tab; re-enter them after reinstalling or restore an add-on backup. There is no separate saved-options fallback.

### Updating from the previous wrapper

Stop the add-on and make a backup before updating. Previous releases stored agent state in the public configuration folder's `arcane/` subdirectory. Move the **contents** of that subdirectory (including hidden files) into the public configuration folder itself before starting this version. Do not overwrite existing files without reviewing them. Supervisor exposes the folder under `/addon_configs/<repository>_<slug>` (some newer tools call it `/app_configs`). Older private `/data` state must be recovered from a backup if it was never migrated to the public folder.

Keep the Manager URL, token and transport entered in the Configuration tab. The old public `options.json` file is no longer read. Automatic state migration and pairing recovery were removed with the startup wrapper. Restart after changing options.

For Docker permission errors, verify Protection mode is off. Supervisor mounts the Docker socket at `/run/docker.sock`; the agent must use `DOCKER_HOST=unix:///run/docker.sock`. A `no such file or directory` error mentioning `/var/run/docker.sock` indicates the old configuration. After installing the corrected package, stop and start the add-on so Supervisor recreates its container with the updated environment. For pairing failures, check Manager URL, token, TLS and outbound connectivity. Polling Standby is healthy.
