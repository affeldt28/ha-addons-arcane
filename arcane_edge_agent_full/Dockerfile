# Package releases are independent of the pinned upstream Arcane release.
ARG BUILD_FROM=alpine:3.23



FROM ghcr.io/getarcaneapp/agent:v2.17.1 AS agent



FROM ${BUILD_FROM}

RUN apk add --no-cache ca-certificates jq tzdata \
    && mkdir -p /app \
    && ln -s /config/arcane /app/data

COPY --from=agent /app/arcane-agent /app/arcane-agent
COPY rootfs /

RUN chmod 0755 /usr/local/bin/run-full

ARG BUILD_VERSION=2.17.1
ARG BUILD_ARCH

LABEL \
    io.hass.name="${BUILD_NAME}" \
    io.hass.description="${BUILD_DESCRIPTION}" \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version="${BUILD_VERSION}" \
    com.getarcaneapp.arcane.agent="true"


ENV ARCANE_IN_CONTAINER=true GIN_MODE=release PORT=3553

WORKDIR /app
ENTRYPOINT ["/usr/local/bin/run-full"]
