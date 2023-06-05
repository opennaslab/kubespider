FROM python:3.9-alpine

ENV HOME="/app" \
    PUID=1000 \
    PGID=1000 \
    UMASK=022 \
    TZ=Asia/Shanghai

WORKDIR /app

RUN set -ex \
    && apk add --no-cache \
        nodejs \
        npm \
        bash \
        su-exec \
        tzdata \
        shadow \
        git \
    && git clone -b main https://github.com/imgyh/tiktok.git /app \
    && mkdir -p /app/downloads \
    && mkdir -p /app/config \
    && python3 -m pip install --upgrade pip \
    && pip install -r requirements_docker.txt \
    && addgroup -S tiktokdlp -g 911 \
    && adduser -S tiktokdlp -G tiktokdlp -h /app -u 911 -s /bin/bash tiktokdlp \
    && rm -rf \
        /app/.git \
        /app/.github \
        /app/.cache \
        /tmp/*

COPY ./app ./
COPY --chmod=755 entrypoint.sh /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]

CMD ["python3", "/app/app.py"]

EXPOSE 3083
