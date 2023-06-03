# syntax=docker/dockerfile:1

FROM nikolaik/python-nodejs:python3.10-nodejs20-slim

WORKDIR /app
COPY ./kubespider ./kubespider
COPY ./.config ./.config_template
COPY requirements.txt ./

ENV HOME="/app" \
    PUID=1000 \
    PGID=1000 \
    UMASK=022

RUN set -ex \
    && apk add --no-cache \
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

CMD ["python3", "/app/kubespider/app.py"]

VOLUME /app/.config

EXPOSE 3080