FROM cesign/youget-base:latest

WORKDIR /root
COPY requirements.txt ./
COPY app app
RUN mkdir -p /root/downloads
RUN mkdir -p /root/config

RUN python3 -m pip install --upgrade pip \
    && pip install -r requirements.txt \
    && rm -rf requirements.txt

EXPOSE 3081

CMD ["python3", "/root/app/app.py"]
