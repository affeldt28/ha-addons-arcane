# Full Access setup

> **WARNING: unrestricted Docker control. The connected Manager can change or delete containers, images, networks and volumes, including resources used by Home Assistant. This can stop Home Assistant or cause data loss. Only connect to a Manager you trust.**

1. Install **Arcane Agent (Full Access)** only if you intend to grant host Docker control.
2. In your separate Arcane Manager, create an Edge environment. If you also run Monitor Only, use a different environment and token.
3. Set `MANAGER_API_URL`, `AGENT_TOKEN` and `EDGE_TRANSPORT` in Configuration. Poll is the default; auto, websocket and grpc are also available. Use HTTPS for remote connections.
4. Disable Protection mode to permit Docker socket access. Start the add-on and confirm it connects. Start on boot is off by default; enable it after testing.

## Features and host limits

This package runs the unmodified official Arcane agent as root with `DOCKER_HOST=unix:///var/run/docker.sock`. There is no method/path proxy. Container deployment, start/stop/restart, deletion, exec/terminal, image management, networks and volumes are available through the agent, subject to your Arcane user permissions and Docker host capabilities.

Host filesystem browsing, arbitrary Compose bind mounts, hardware access, GPU support and Swarm networking depend on the host configuration. This package does not mount the host root or Docker volume directory into the agent. Docker resolves bind source paths on the host, not relative to the agent container. Direct Docker access can itself create containers with additional host mounts or privileges.

Supervisor owns Home Assistant and its add-on containers. Use Home Assistant for their lifecycle and updates. Arcane agent self-update and automatic pruning/updating of Supervisor-managed resources may conflict with Supervisor. The package intentionally adds no Supervisor API permissions, exposed host ports or blanket hardware access; Docker access already grants substantial host control.

This is an Edge agent, not the Arcane Manager web application.

## Persistence and troubleshooting

Private add-on data is mounted at `/app/data` and included in cold backups. Protect backups and options because they contain credentials. Restart after option changes.

For Docker permission errors, verify Protection mode is off. For pairing failures, check Manager URL, token, TLS and outbound connectivity. Polling Standby is healthy.
