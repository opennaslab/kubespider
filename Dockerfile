# syntax=docker/dockerfile:1

FROM python:3.10-alpine

RUN touch /.dockerenv

WORKDIR /app
COPY ./kubespider ./kubespider
COPY ./.config ./.config_template
COPY requirements.txt ./

ENV HOME="/app" \
    PUID=1000 \
    PGID=1000 \
    UMASK=022 \
    TZ=Asia/Shanghai

RUN set -ex \
    && apk add --no-cache \
        nodejs \
        npm \
        bash \
        su-exec \
        tzdata \
        shadow \
    && python3 -m pip install --upgrade pip \
    && pip install -r requirements.txt \
    && addgroup -S kubespider -g 911 \
    && adduser -S kubespider -G kubespider -h /app -u 911 -s /bin/bash kubespider \
    && rm -rf \
        /app/.cache \
        /tmp/*

COPY --chmod=755 entrypoint.sh /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]

CMD ["server"]

VOLUME /app/.config

EXPOSE 3080