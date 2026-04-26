# syntax=docker/dockerfile:1.7

ARG PICOCLAW_REPO=https://github.com/sipeed/picoclaw.git
ARG PICOCLAW_REF=main

FROM golang:1.25-alpine AS picoclaw-builder

ARG PICOCLAW_REPO
ARG PICOCLAW_REF

RUN apk add --no-cache ca-certificates git make nodejs npm
RUN npm install -g pnpm

RUN git clone --depth 1 --branch "${PICOCLAW_REF}" "${PICOCLAW_REPO}" /src || \
    (git clone --depth 1 "${PICOCLAW_REPO}" /src && \
     git -C /src fetch --depth 1 origin "${PICOCLAW_REF}" && \
     git -C /src checkout FETCH_HEAD)

WORKDIR /src
RUN make build
RUN make build-launcher

FROM python:3.12-alpine

RUN apk add --no-cache ca-certificates curl tzdata wget

ENV PICOCLAW_HOME=/data/picoclaw \
    PICOCLAW_CONFIG=/data/picoclaw/config.json \
    PICOCLAW_BINARY=/usr/local/bin/picoclaw \
    PICOCLAW_GATEWAY_HOST=0.0.0.0 \
    PICOCLAW_GATEWAY_PORT=18790 \
    T3MT_HOST=http://t3fap:8521 \
    T3MT_AUTOMATION_MODE=full-access \
    T3FAP_ASSISTANT_MODEL_NAME=gpt-5.4 \
    T3FAP_ASSISTANT_MODEL=openai/gpt-5.4 \
    T3FAP_ASSISTANT_API_BASE=https://api.openai.com/v1

WORKDIR /opt/t3fap-ai-assistant

COPY --from=picoclaw-builder /src/build/picoclaw /usr/local/bin/picoclaw
COPY --from=picoclaw-builder /src/build/picoclaw-launcher /usr/local/bin/picoclaw-launcher
COPY runtime ./runtime
COPY skills ./skills

RUN chmod +x /usr/local/bin/picoclaw \
    /usr/local/bin/picoclaw-launcher \
    ./runtime/t3fap_assistant_runtime.py \
    ./skills/t3mt-api/scripts/t3mt-api.py \
    ./skills/t3mt-cli/scripts/t3mt-cli.py

VOLUME ["/data/picoclaw"]
EXPOSE 18800 18790

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD wget -q --spider http://127.0.0.1:18800 || exit 1

ENTRYPOINT ["python", "/opt/t3fap-ai-assistant/runtime/t3fap_assistant_runtime.py"]
