# Runtime images are pinned; Home Assistant builds for the selected architecture.
ARG BUILD_FROM=alpine:3.23
FROM ghcr.io/getarcaneapp/agent:v2.16.1 AS agent
FROM ghcr.io/wollomatic/socket-proxy:1.13.1 AS proxy
FROM ${BUILD_FROM}

RUN apk add --no-cache ca-certificates jq su-exec tzdata \
    && mkdir -p /app /etc/arcane-monitor \
    && ln -s /data/arcane /app/data

COPY --from=agent /app/arcane-agent /app/arcane-agent
COPY --from=proxy /socket-proxy /usr/local/bin/socket-proxy

# Home Assistant Community Apps convention: install container files through rootfs.
COPY rootfs /
RUN chmod 0755 /usr/local/bin/run-monitor

ARG BUILD_ARCH
ARG BUILD_VERSION=2.16.1-2
ARG BUILD_NAME="Arcane Edge Agent (Monitor Only)"
ARG BUILD_DESCRIPTION="Arcane Edge agent with filtered Docker monitoring access"
ARG BUILD_DATE
ARG BUILD_REF
LABEL \
    io.hass.name="${BUILD_NAME}" \
    io.hass.description="${BUILD_DESCRIPTION}" \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version="${BUILD_VERSION}" \
    org.opencontainers.image.title="${BUILD_NAME}" \
    org.opencontainers.image.description="${BUILD_DESCRIPTION}" \
    org.opencontainers.image.created="${BUILD_DATE}" \
    org.opencontainers.image.revision="${BUILD_REF}" \
    org.opencontainers.image.version="${BUILD_VERSION}"

# This image uses Docker's init (config.json init: true), rather than S6.
WORKDIR /app
ENTRYPOINT ["/usr/local/bin/run-monitor"]
