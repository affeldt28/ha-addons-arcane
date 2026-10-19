# Setup

1. Publish and add this repository as described in the repository README. The maintainer must configure the repository URL first.
2. Install both **Arcane Read-only Docker Proxy** and **Arcane Edge Agent (Monitoring)**.
3. Disable Protection mode **only for the proxy**, because Home Assistant requires that for Docker socket access. Keep Protection mode enabled for the agent. Start the proxy first.
4. In an existing Arcane Manager, open **Environments → Add Environment → Edge** and generate the agent configuration.
5. In the agent's Configuration tab, enter the generated `MANAGER_API_URL` and `AGENT_TOKEN`. Leave the preconfigured `DOCKER_HOST` pointing to the proxy. Use HTTPS for a remote Manager. Keep `EDGE_TRANSPORT: poll` unless your Manager requires another transport.
6. Start the agent. Confirm the environment connects in Arcane. In polling mode, Standby is healthy; Online means an active tunnel.

The hostname allowlist on the proxy limits access to this agent. If you install from a different URL or branch, re-run the repository configuration tool with that exact URL (including `#branch` if used). Do not use a broad client IP allowlist or expose port 2375.

## What read-only means

Docker-changing requests are blocked at the proxy. Monitoring includes container metadata, logs, stats, process lists, image metadata, volumes and networks. Deploying, updating, restarting, stopping, deleting, pruning and terminal sessions cannot work. File/archive downloads and image exports are blocked too. Swarm views and features that need other endpoints may show errors. Arcane can still save its own settings and state; this is read-only access to Docker, not an immutable agent filesystem.

Inspection and logs can contain passwords, environment variables and other sensitive data. Only connect to a trusted Arcane Manager. The proxy itself has real Docker socket access; its protection relies on its process and fixed allowlist. It runs separately so the agent cannot bypass the filter by opening the socket directly.

## State, backups and updates

Agent state lives in persistent private add-on storage at `/app/data`. Home Assistant cold backups stop the agent briefly and include this state. Options and backups contain your token. Update and restart the agent through Home Assistant; Arcane self-upgrade is blocked.

## Troubleshooting

- Permission denied: check Protection mode is off for the proxy only, and restart it.
- Connection refused or forbidden: start the proxy first and verify `DOCKER_HOST` and `SP_ALLOWFROM` match the installed add-on hostnames. The publication tool sets these from the repository URL.
- Pairing errors: check token, Manager URL, TLS and outbound connectivity. Try polling if the reverse proxy cannot handle a persistent tunnel.
- Action buttons return errors: expected for monitoring-only mode. Missing monitoring data may indicate an endpoint outside the allowlist; report the path for review rather than allowing all requests.

Restart an add-on after changing its configuration.
