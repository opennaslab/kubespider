FROM python:3.9-alpine

ENV HOME="/app" \
    PUID=1000 \
    PGID=1000 \
    UMASK=022 \
    TZ=Asia/Shanghai

WORKDIR /app

COPY ./app ./
COPY requirements.txt ./

RUN set -ex \
    && apk add --no-cache \
        nodejs \
        npm \
        bash \
        su-exec \
        tzdata \
        shadow \
    && mkdir -p /app/downloads \
    && mkdir -p /app/config \
    && python3 -m pip install --upgrade pip \
    && pip install -r requirements.txt \
    && addgroup -S tiktokdlp -g 911 \
    && adduser -S tiktokdlp -G tiktokdlp -h /app -u 911 -s /bin/bash tiktokdlp

COPY --chmod=755 entrypoint.sh /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]

CMD ["python3", "/app/app.py"]

EXPOSE 3083
