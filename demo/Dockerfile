# Dockerfile
ARG PYTHON_VERSION=3.8-slim-buster

FROM python:${PYTHON_VERSION}
ENV PYTHONUNBUFFERED=1

RUN mkdir -p /opt/sample-rpc-service
RUN apt-get update -qq -y \
    && apt-get -y install gcc g++ libffi-dev python3-dev make \
    && mkdir -p /opt/sample-rpc-service

COPY ./demo/requirements.txt ./
RUN pip install -r requirements.txt

COPY ./demo/easy_pyrpc-*.whl ./
RUN pip install ./easy_pyrpc-*.whl

WORKDIR /opt/sample-rpc-service

COPY demo/sample_rpc_service.py ./
COPY VERSION ./
COPY demo/uwsgi.ini ./

EXPOSE 5000

CMD ["uwsgi", "uwsgi.ini"]