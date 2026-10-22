# Changelog

## 2.16.1-3

- Move agent state and saved pairing settings to the public add-on config folder, migrating existing `/data/arcane` state on first start.
- Reuse retained pairing settings after reinstall when Configuration contains blank defaults.

## 2.16.1-2

- Fix agent startup by resolving su-exec before sanitizing the environment and including sbin directories in PATH.
- Suppress expected connection-refused messages while waiting for the proxy to start; keep final readiness failures visible.
- Test the complete monitor startup with a fake agent, including unprivileged execution and shutdown.

## 2.16.1-1

- Adopt the SSH add-on packaging conventions: rootfs layout, build labels, configuration help and shell linting.
- Make Monitor Only a single installable add-on with a loopback Docker API proxy.
- Run Arcane as an unprivileged user; fail closed if it can open the real socket.
- Remove the unreleased companion-proxy layout; state path changes to `/data/arcane`.
