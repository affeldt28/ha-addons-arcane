# Supervisor adds Home Assistant labels from config.yaml at build time.
# Preserve the official runtime; a static shell maps legacy UI option names.
ARG BUILD_FROM=getarcaneapp/agent:v3.0.1
FROM --platform=$BUILDPLATFORM golang:1.27-trixie AS migration-builder
ARG TARGETARCH
COPY migration /src
RUN go test /src/save.go /src/save_test.go
RUN CGO_ENABLED=0 GOOS=linux GOARCH=${TARGETARCH} go build -o /migration-save /src/save.go
FROM busybox:1.37.0-musl AS migration-shell
FROM ${BUILD_FROM}
COPY --from=migration-shell /bin/busybox /usr/local/bin/busybox
COPY --from=migration-builder /migration-save /usr/local/bin/migration-save
COPY rootfs /
ENTRYPOINT ["/usr/local/bin/busybox", "sh", "/usr/local/bin/run-full"]
CMD ["./arcane-agent"]
