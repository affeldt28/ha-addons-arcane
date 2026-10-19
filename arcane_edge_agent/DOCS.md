# Monitor Only setup

1. Install this add-on. No companion proxy is needed.
2. In your separate Arcane Manager, create an Edge environment and generate its agent configuration.
3. Set `MANAGER_API_URL`, `AGENT_TOKEN` and `EDGE_TRANSPORT` in the Configuration tab. Poll is the default; auto, websocket and grpc are also available. Use HTTPS over untrusted networks.
4. Disable Protection mode, then start the add-on. Home Assistant requires this to mount Docker's socket, even though the Arcane process uses a filter.
5. Confirm the environment connects. In polling mode, Standby is healthy; Online indicates an active tunnel. Enable Start on boot after testing.

## Access boundary

The built-in proxy alone runs as root and opens the real Docker socket. Arcane runs as UID/GID 65532 with no supplementary groups and receives a clean environment pointing Docker at `127.0.0.1:2375`. Startup refuses to continue if that user has write permission on the real socket, as Unix socket connections require write permission. The proxy accepts only loopback clients and an explicit GET/HEAD allowlist, and cannot be reconfigured through add-on options. No proxy port is exposed to other containers or the host.

This permits container lists, inspect, logs, stats, top; image/network/volume metadata; Docker info, events and disk usage. Write methods, exec/attach, file archives, image exports, builds, pruning and Swarm administration are blocked. Unsupported Arcane screens may display errors; do not broaden the policy simply to remove those errors.

The add-on still contains a privileged proxy process. A compromise of that process would have real Docker access. Metadata and logs can expose secrets. Install Full Access only if you want a separate environment with unrestricted control.

## Persistence and updates

State is stored under `/data/arcane`, linked to `/app/data`, and included in cold add-on backups. Backups stop the add-on briefly and contain state and credentials. Restart after changing options. Use Home Assistant for updates.

If you used the earlier unreleased two-container prototype, back up first: its data lived directly under `/app/data` and is not automatically migrated into this layout. Remove the obsolete standalone proxy; this version no longer uses it.

## Troubleshooting

- Missing socket: disable Protection mode and restart.
- Socket accessible to the agent user: startup deliberately refuses to run. Correct host socket ownership/permissions through the host administrator; this add-on never changes them.
- Pairing issues: check token, URL, certificates and outbound connectivity; try poll if tunnel transport fails.
- Forbidden Docker actions: expected for monitoring-only mode. Report missing monitoring endpoints for review.
