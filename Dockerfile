# base image
FROM python:3.6-slim

USER root

RUN mkdir /code
WORKDIR /code
ADD . /code
RUN chmod -R 777 /code

# install needed packages
RUN apt-get update \
    && apt-get install -y python-psycopg2 build-essential postgresql-client \
    && pip install --trusted-host pypi.python.org -r requirements.txt
