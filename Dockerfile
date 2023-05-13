FROM nikolaik/python-nodejs:python3.10-nodejs20-slim

WORKDIR /root
COPY ./kubespider ./kubespider
COPY ./.config ./.config
COPY requirements.txt ./

RUN python3 -m pip install --upgrade pip \
    && pip install -r requirements.txt \
    && rm -rf requirements.txt

EXPOSE 3080

CMD ["python3", "/root/kubespider/app.py"]