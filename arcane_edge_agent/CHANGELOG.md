# Changelog

## 2.16.1-1

- Adopt the SSH add-on packaging conventions: rootfs layout, build labels, configuration help and shell linting.
- Make Monitor Only a single installable add-on with a loopback Docker API proxy.
- Run Arcane as an unprivileged user; fail closed if it can open the real socket.
- Remove the unreleased companion-proxy layout; state path changes to `/data/arcane`.
