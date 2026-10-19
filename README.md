# Arcane Monitoring for Home Assistant

Community add-ons for running an Arcane Edge Agent on Home Assistant OS with **monitoring-only Docker access**. Requires Supervisor and an existing Arcane Manager. Independent of Home Assistant and Arcane; experimental until validated on a real HA OS system.

The repository contains two add-ons:

- **Arcane Read-only Docker Proxy** is the only component with the real Docker socket. It forwards an explicit list of GET inspection endpoints and HEAD health checks. All other requests are denied.
- **Arcane Edge Agent (Monitoring)** connects outbound to your Manager and uses the proxy. It has no Docker socket, Supervisor API permission, host directory mounts, or exposed host ports. Leave its Protection mode enabled.

The proxy allows container listing, inspection, logs, statistics and processes; image, network and volume metadata; Docker information, events and disk usage. It denies creation, updates, restarts, deletion, pruning, exec, attach, archive/file downloads, image exports, builds and Swarm administration. Arcane may still display action buttons, but Docker-changing actions fail.

## Publish

1. Choose a stable public Git repository URL.
2. Run `python3 tools/configure_repository.py https://github.com/YOUR_ACCOUNT/ha-addons-arcane` with the actual URL you will add to Home Assistant. This sets metadata, proxy hostname and the agent-only client allowlist. Run this before installing, since the repository URL determines Home Assistant's add-on IDs.
3. Commit and push this directory to that repository. The proxy builds on the Home Assistant device; the agent uses Arcane's official image. No personal container registry is required.
4. Add the same URL under Home Assistant **Settings → Apps → Install app → ⋮ → Repositories** (older versions: **Settings → Add-ons → Add-on Store**).
5. Follow [setup instructions](arcane_edge_agent/DOCS.md).

Until step 2, the proxy allows only localhost and the agent has an intentionally nonfunctional proxy hostname. Installation therefore fails closed.

## Validation and maintenance

Run `python3 tools/check_policy.py` for configuration and access-policy checks. With Docker running, run `python3 tools/test_proxy.py` to exercise the actual proxy against a fake Docker socket; it never connects to the real Docker daemon socket. GitHub Actions runs both checks. Live Arcane pairing and Home Assistant installation still need a test device.

Keep Manager and agent versions compatible. Update add-ons through Home Assistant, not Arcane. A new upstream agent tag requires updating the agent version; proxy updates require updating the Dockerfile tag and incrementing its add-on version.

[Arcane proxy documentation](https://getarcane.app/docs/security/socket-proxy) · [Home Assistant repository documentation](https://contributors.home-assistant.io/apps/guides/repository/)
