FROM nikolaik/python-nodejs:python3.10-nodejs20-alpine

WORKDIR /kubespider
COPY ./kubespider ./kubespider
COPY ./.config ./.config_template
COPY requirements.txt ./

ENV HOME="/kubespider" \
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
    && adduser -S kubespider -G kubespider -h /kubespider -u 911 -s /bin/bash kubespider \
    && rm -rf \
        /kubespider/.cache \
        /tmp/*

COPY --chmod=755 entrypoint.sh /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]

CMD ["python3", "/kubespider/kubespider/app.py"]

VOLUME /kubespider/.config

EXPOSE 3080