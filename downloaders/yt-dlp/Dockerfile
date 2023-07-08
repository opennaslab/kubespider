# syntax=docker/dockerfile:1

FROM python:3.10-alpine

ENV HOME="/app" \
    PUID=1000 \
    PGID=1000 \
    UMASK=022 \
    TZ=Asia/Shanghai

WORKDIR /app

COPY requirements.txt ./
COPY app app

RUN set -ex \
    && apk add --no-cache \
        bash \
        su-exec \
        tzdata \
        shadow \
        ffmpeg \
    && mkdir -p /app/downloads \
    && mkdir -p /app/config \
    && python3 -m pip install --upgrade pip \
    && pip install -r requirements.txt \
    && addgroup -S ytdlp -g 911 \
    && adduser -S ytdlp -G ytdlp -h /app -u 911 -s /bin/bash ytdlp \
    && rm -rf \
        /app/.cache \
        /tmp/*

COPY --chmod=755 entrypoint.sh /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]

CMD ["server"]

EXPOSE 3082