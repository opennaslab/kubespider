FROM python:3.10-buster AS build

RUN mkdir /install
WORKDIR /install
COPY requirements.txt .
RUN python3 -m pip install --upgrade pip \
    && pip install -r requirements.txt --prefix="/install"

FROM python:3.10-alpine

WORKDIR /root

COPY --from=build /install /usr/local
ADD ./.kubespider /root

RUN apk add curl

ENV TZ=Asia/Shanghai

EXPOSE 3080

CMD ["kubespider"]