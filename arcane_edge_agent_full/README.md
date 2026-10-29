<img src="https://raw.githubusercontent.com/affeldt28/ha-addons-arcane/main/arcane_edge_agent_full/logo.png" alt="Arcane" width="400">

# Arcane Agent · Full Access

Manage the Docker host running Home Assistant from your existing Arcane dashboard. This variant uses the official Arcane Edge agent with direct Docker access, so you can inspect resources and perform management actions from one place.

> **WARNING — Full Docker control.** The connected Arcane Manager can change or delete containers, images, networks and volumes, including resources used by Home Assistant and Supervisor. This can interrupt your smart home or cause data loss. Connect only to a Manager you trust. For visibility without management actions, choose **Arcane Agent (Monitor)**.

## What you can do

- **Monitor:** inspect containers, view logs and follow resource statistics.
- **Manage containers:** deploy, start, stop, restart, update and remove them.
- **Open terminals:** use Arcane's container exec and terminal features.
- **Manage Docker resources:** work with images, networks and volumes.

Features depend on your Arcane permissions and the Docker host's capabilities. The add-on does not mount the host root or Docker volumes directory into the agent; host files, bind mounts, devices and Swarm networking still depend on the host configuration.

## How it connects

The Edge agent opens an **outbound connection to your Arcane Manager**. No inbound host port is published. Use the Manager's existing dashboard to manage this environment; this add-on does not include the Arcane Manager web application.

## Get started

1. In Arcane Manager, choose **Environments → Add Environment → Edge** and generate an agent configuration.
2. In this add-on's **Configuration** tab, enter the Manager URL and token. The default **poll** transport works without a persistent tunnel.
3. Read the warning above, turn off **Protection mode**, and start the add-on.
4. Confirm that the environment connects in Arcane. **Standby** is healthy in polling mode. Enable **Start on boot** after testing.

You need Home Assistant with Supervisor, an existing Arcane Manager and a supported 64-bit host (amd64 or aarch64). Use a separate environment and token if you also run the monitoring variant.

## Keep Home Assistant in control of its own containers

Use Home Assistant to update and manage Supervisor-owned containers and these add-ons. Arcane self-updates, automatic updates or pruning of those resources may conflict with Supervisor. Docker socket access is powerful even without extra host directory mounts.

The image uses the official Arcane runtime and entrypoint, adding only Home Assistant labels. Agent state is stored in the public add-on config folder mounted at `/app/data`. Pairing settings come directly from the Configuration tab. Add-on backups include configuration and state. After reinstalling, re-enter pairing settings or restore a backup. When updating from the previous wrapper, follow the storage migration instructions in the documentation.

[Setup, options and troubleshooting](https://github.com/affeldt28/ha-addons-arcane/blob/main/arcane_edge_agent_full/DOCS.md) · [Arcane documentation](https://getarcane.app/docs/remote/environments) · [Report an issue](https://github.com/affeldt28/ha-addons-arcane/issues)

Independent community add-on. Arcane artwork belongs to the upstream project; [license and attribution](https://github.com/affeldt28/ha-addons-arcane/tree/main/branding).
