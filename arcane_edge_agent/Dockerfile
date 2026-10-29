# Runtime images are pinned; Home Assistant builds for the selected architecture.
ARG BUILD_FROM=alpine:3.23

FROM ghcr.io/getarcaneapp/agent:v2.17.1 AS agent
FROM ghcr.io/wollomatic/socket-proxy:1.13.1 AS proxy
FROM ${BUILD_FROM}

RUN apk add --no-cache ca-certificates jq su-exec tzdata \
    && mkdir -p /app /etc/arcane-monitor \
    && ln -s /config/arcane /app/data

COPY --from=agent /app/arcane-agent /app/arcane-agent
COPY --from=proxy /socket-proxy /usr/local/bin/socket-proxy

# Home Assistant Community Apps convention: install container files through rootfs.
COPY rootfs /
RUN chmod 0755 /usr/local/bin/run-monitor

# Supervisor supplies Home Assistant image labels from config.yaml.
# This image uses Docker's init (config.yaml init: true), rather than S6.
WORKDIR /app
ENTRYPOINT ["/usr/local/bin/run-monitor"]
