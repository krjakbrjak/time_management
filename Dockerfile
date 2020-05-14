FROM python:3.8.2 as dev

RUN mkdir -p /opt/app
COPY requirements.txt /opt/app

WORKDIR /opt/app
RUN pip install -r requirements.txt
