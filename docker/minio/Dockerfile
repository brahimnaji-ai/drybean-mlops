ARG GO_IMAGE=golang:1.24.8-alpine3.22
FROM ${GO_IMAGE} AS build

ARG MINIO_VERSION=RELEASE.2025-10-15T17-29-55Z
ARG MC_VERSION=RELEASE.2025-08-13T08-35-41Z

ENV GOMAXPROCS=2 GOGC=50

RUN apk add --no-cache ca-certificates git
WORKDIR /src
RUN git clone --depth 1 --branch "${MINIO_VERSION}" https://github.com/minio/minio.git minio \
    && git clone --depth 1 --branch "${MC_VERSION}" https://github.com/minio/mc.git mc \
    && mkdir -p /out

RUN cd /src/minio \
    && MINIO_LDFLAGS="$(MINIO_RELEASE=RELEASE go run -p 1 buildscripts/gen-ldflags.go "${MINIO_VERSION#RELEASE.}")" \
    && CGO_ENABLED=0 go build -p 1 -tags kqueue -trimpath -ldflags "${MINIO_LDFLAGS}" -o /out/minio .
RUN cd /src/mc && CGO_ENABLED=0 go build -p 1 -trimpath -ldflags "-s -w" -o /out/mc .

FROM alpine:3.22.2 AS runtime

RUN apk add --no-cache ca-certificates \
    && addgroup -S -g 10001 minio \
    && adduser -S -D -H -u 10001 -G minio minio \
    && mkdir -p /data /home/minio/.mc \
    && chown -R minio:minio /data /home/minio

COPY --from=build /out/minio /usr/local/bin/minio
COPY --from=build /out/mc /usr/local/bin/mc
COPY --from=build /src/minio/LICENSE /licenses/MINIO-LICENSE
COPY --from=build /src/mc/LICENSE /licenses/MC-LICENSE

ENV HOME=/home/minio
VOLUME ["/data"]
USER 10001:10001
ENTRYPOINT ["/usr/local/bin/minio"]
CMD ["server", "/data", "--console-address", ":9001"]
