FROM ghcr.io/getarcaneapp/agent:v2.16.1 AS agent
FROM ghcr.io/wollomatic/socket-proxy:1.13.1 AS proxy
FROM alpine:3.23
RUN apk add --no-cache ca-certificates jq su-exec tzdata \
    && mkdir -p /app /etc/arcane-monitor \
    && ln -s /data/arcane /app/data
COPY --from=agent /app/arcane-agent /app/arcane-agent
COPY --from=proxy /socket-proxy /usr/local/bin/socket-proxy
COPY policy.json /etc/arcane-monitor/policy.json
COPY run.sh /usr/local/bin/run-monitor
RUN chmod 0755 /usr/local/bin/run-monitor
WORKDIR /app
ENTRYPOINT ["/usr/local/bin/run-monitor"]
