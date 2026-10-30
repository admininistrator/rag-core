# syntax=docker/dockerfile:1.7@sha256:a57df69d0ea827fb7266491f2813635de6f17269be881f696fbfdf2d83dda33e
FROM golang:1.24-alpine@sha256:8bee1901f1e53001859bf9ec42c388efd42db8724ec35e5d3fc827f8d55c7b3f AS builder
RUN apk add --no-cache git
RUN CGO_ENABLED=0 go install github.com/minio/mc@RELEASE.2025-08-13T08-35-41Z

FROM alpine:3.22@sha256:2e0b81d60597f449baa568eb7de877e68d90be71253c51121bf95ef6722d56a7
RUN apk add --no-cache ca-certificates
COPY --from=builder /go/bin/mc /usr/local/bin/mc
ENTRYPOINT ["mc"]

