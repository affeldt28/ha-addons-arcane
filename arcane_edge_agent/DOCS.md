# Monitor Only setup

1. Install this add-on. No companion proxy is needed.
2. In your separate Arcane Manager, create an agent enrollment token and generate its agent configuration.
3. Set `ARCANE_MANAGER_API_URL`, `ARCANE_AGENT_TOKEN` and `ARCANE_AGENT_TRANSPORT` in the Configuration tab. Auto is the default; websocket and grpc are also available. Use HTTPS over untrusted networks.
4. Disable Protection mode, then start the add-on. Home Assistant requires this to mount Docker's socket, even though the Arcane process uses a filter.
5. Confirm the environment connects. Online indicates an active tunnel. Enable Start on boot after testing.

## Access boundary

The built-in proxy alone runs as root and opens the real Docker socket. Arcane runs as UID/GID 65532 with no supplementary groups and receives a clean environment pointing Docker at `127.0.0.1:2375`. Startup refuses to continue if that user has write permission on the real socket, as Unix socket connections require write permission. The proxy accepts only loopback clients and an explicit GET/HEAD allowlist, and cannot be reconfigured through add-on options. No proxy port is exposed to other containers or the host.

This permits container lists, inspect, logs, stats, top; image/network/volume metadata; Docker info, events and disk usage. Write methods, exec/attach, file archives, image exports, builds, pruning and Swarm administration are blocked. Unsupported Arcane screens may display errors; do not broaden the policy simply to remove those errors.

The add-on still contains a privileged proxy process. A compromise of that process would have real Docker access. Metadata and logs can expose secrets. Install Full Access only if you want a separate environment with unrestricted control.

## Persistence and updates

State is stored in `/config/arcane` inside the container, linked to `/app/data`. Pairing settings are saved in `/config/options.json` with owner-only permissions. Supervisor exposes this public folder under `/addon_configs/<repository>_<slug>` (some newer tools call it `/app_configs`). It is included in cold add-on backups.

On first start after updating, existing private state is copied automatically; retained public state is never overwritten. **Update and start the add-on before uninstalling** so migration can run. When uninstalling, leave the option to remove the public configuration folder unchecked. Reinstall from the same repository with the same slug to reuse the folder. Deleting that folder also deletes the retained state.

After reinstall, leave Manager URL and token blank to reuse saved pairing settings, including transport. To replace them, enter both fields in the Configuration tab; valid settings are saved at startup. Home Assistant's Configuration form itself is not restored from this file. Backups and the public folder contain credentials; protect them accordingly. Restart after changing options.

Storage follows [Home Assistant's public configuration folder guidance](https://contributors.home-assistant.io/blog/2023/11/06/public-addon-config/) and [configuration file lifecycle](https://contributors.home-assistant.io/apps/guides/options/#configuration-files-for-users).

If you used the earlier unreleased two-container prototype, back up first: its data lived directly under `/app/data` and is not automatically migrated into this layout. Remove the obsolete standalone proxy; this version no longer uses it.

## Troubleshooting

- Missing socket: disable Protection mode and restart.
- Socket accessible to the agent user: startup deliberately refuses to run. Correct host socket ownership/permissions through the host administrator; this add-on never changes them.
- Pairing issues: check token, URL, certificates and outbound connectivity; try websocket if gRPC transport fails.
- Forbidden Docker actions: expected for monitoring-only mode. Report missing monitoring endpoints for review.

## Upgrading from Arcane 2

Back up first and upgrade the Manager and agents to Arcane 2.17.3, starting each once, before upgrading the Manager to Arcane 3. The add-on automatically reuses old `MANAGER_API_URL` and `AGENT_TOKEN` Configuration fields when the corresponding `ARCANE_*` fields are blank, and uses `auto` instead of polling. It also corrects an escaped `http\://` or `https\://` prefix. Explicit nonempty new URL and token fields take precedence. Existing edge-agent API keys remain usable; former direct agents need a new enrollment token. At startup, the add-on saves the migrated values into the new Home Assistant Configuration fields and removes the legacy fields. Refresh Configuration after starting. If Supervisor cannot save the fields, startup continues with the migrated settings and saving retries on the next restart. Keep the public configuration folder to preserve state.
