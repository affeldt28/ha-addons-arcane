# Package releases are independent of the pinned upstream Arcane release.
FROM ghcr.io/getarcaneapp/agent:v2.16.1 AS agent
FROM alpine:3.23
RUN apk add --no-cache ca-certificates jq tzdata \
    && mkdir -p /app \
    && ln -s /config/arcane /app/data
COPY --from=agent /app/arcane-agent /app/arcane-agent
COPY rootfs /
RUN chmod 0755 /usr/local/bin/run-full
ARG BUILD_VERSION=2.16.1-1
ARG BUILD_ARCH
LABEL io.hass.type="addon" \
    io.hass.version="${BUILD_VERSION}" \
    io.hass.arch="${BUILD_ARCH}" \
    com.getarcaneapp.arcane.agent="true"
ENV ARCANE_IN_CONTAINER=true GIN_MODE=release PORT=3553
WORKDIR /app
ENTRYPOINT ["/usr/local/bin/run-full"]
