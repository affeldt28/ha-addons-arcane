<img src="https://raw.githubusercontent.com/affeldt28/ha-addons-arcane/main/arcane_edge_agent/logo.png" alt="Arcane" width="400">

# Arcane Agent · Monitor

Keep an eye on your Home Assistant host from your existing Arcane dashboard. View containers, live resource usage and logs through an outbound Edge connection, with Docker changes blocked by a built-in proxy.

## What you can see

- **Containers:** status, configuration, running processes and logs.
- **Resource usage:** container statistics and Docker disk usage.
- **Docker resources:** images, networks and volume metadata.
- **Host activity:** Docker information and events.

This is useful when you want the Home Assistant host alongside your other Docker environments in Arcane, without giving the agent permission to deploy, restart or remove containers.

## How it connects

The agent connects **outbound to your Arcane Manager**. No inbound host port or separate proxy add-on is needed. Open the Arcane Manager you already use to view this environment; this add-on does not provide a separate dashboard inside Home Assistant.

## Get started

1. In Arcane Manager, choose **Environments → Add Environment → Edge** and generate an agent configuration.
2. In this add-on's **Configuration** tab, enter the Manager URL and agent token. Leave the transport on **poll** unless your setup needs another option.
3. Turn off **Protection mode**, start the add-on, and check that the environment appears in Arcane. **Standby** is a healthy state when using polling.

You need Home Assistant with Supervisor, an existing Arcane Manager and a supported 64-bit host (amd64 or aarch64).

## Monitoring, with limits

The filter blocks deployments, start/stop/restart, updates, deletion, pruning, terminal sessions and container file downloads. Arcane may still show action buttons; blocked operations return an error. Some views that need additional Docker endpoints may be unavailable.

**Why Protection mode is off:** Home Assistant requires it to mount the Docker socket. Inside the add-on, only the proxy runs with socket access. The Arcane process runs as a separate unprivileged user and uses the filtered connection. Startup refuses to continue if that user could access the real socket directly.

Container metadata and logs can contain secrets, so connect only to a trusted Manager. The proxy itself remains a privileged component.

## Choose your access level

| Monitor | Full Access |
| --- | --- |
| Inspect containers, logs and statistics | Inspect and manage Docker resources |
| Docker changes blocked | Deploy, restart, update and delete |
| Terminal sessions blocked | Container terminal access available |

For management actions, choose **Arcane Agent (Full Access)** and read its access warning. Each installed variant needs its own Arcane environment and token.

[Setup, options and troubleshooting](https://github.com/affeldt28/ha-addons-arcane/blob/main/arcane_edge_agent/DOCS.md) · [Arcane documentation](https://getarcane.app/docs/remote/environments) · [Report an issue](https://github.com/affeldt28/ha-addons-arcane/issues)

Independent community add-on. Arcane artwork belongs to the upstream project; [license and attribution](https://github.com/affeldt28/ha-addons-arcane/tree/main/branding).
