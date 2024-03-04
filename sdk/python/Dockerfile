FROM python:3.11-alpine

RUN apk add binutils
WORKDIR /app/python
COPY . ./
RUN pip install -r requirements.txt

CMD ./install.sh
