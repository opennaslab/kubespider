FROM python:3.10-buster

WORKDIR /root
COPY ./kubespider ./kubespider
COPY ./.kubespider ./.kubespider
COPY requirements.txt ./

RUN pip install -r requirements.txt \
    && rm -rf requirements.txt

EXPOSE 3080

CMD ["python3", "/root/kubespider/app.py"]