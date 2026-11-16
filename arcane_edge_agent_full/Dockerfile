# Supervisor adds Home Assistant labels from config.yaml at build time.
# Preserve the official runtime; a static shell maps legacy UI option names.
ARG BUILD_FROM=getarcaneapp/agent:v3.0.1
FROM busybox:1.37.0-musl AS migration-shell
FROM ${BUILD_FROM}
COPY --from=migration-shell /bin/busybox /usr/local/bin/busybox
COPY rootfs /
ENTRYPOINT ["/usr/local/bin/busybox", "sh", "/usr/local/bin/run-full"]
CMD ["./arcane-agent"]
