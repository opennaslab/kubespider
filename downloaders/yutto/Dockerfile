# syntax=docker/dockerfile:1

FROM python:3.12-alpine

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
    && apk add --no-cache --virtual=build-dependencies \
        build-base \
        gcc \
        g++ \
        make \
        libffi-dev \
        libc-dev \
        linux-headers \
        postgresql-dev \
    && mkdir -p /app/downloads \
    && mkdir -p /app/config \
    && python3 -m pip install --upgrade pip \
    && pip install -r requirements.txt \
    && addgroup -S yutto -g 911 \
    && adduser -S yutto -G yutto -h /app -u 911 -s /bin/bash yutto \
    && apk del --purge build-dependencies \
    && rm -rf \
        /app/.cache \
        /tmp/*

COPY --chmod=755 entrypoint.sh /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]

CMD ["python3", "/app/app/app.py"]

EXPOSE 3084