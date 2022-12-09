FROM python:3.8.13-slim AS BASE

FROM rasa/rasa:3.2.6-spacy-en

# install dependencies of interest
# RUN python -m pip install rasa==3.2.6 && python -m pip install spacy

# RUN python -m spacy download en_core_web_md

# set workdir and copy data files from disk
# note the latter command uses .dockerignore

USER root

# RUN python -h pip install libpq-dev

WORKDIR /app
ENV HOME=/app


COPY requirements.txt .
# COPY device_bind.sh .
# RUN chmod +x device_bind.sh

RUN apt-get update \
    && apt-get -y install libpq-dev gcc

RUN python -m pip install -r requirements.txt

# RUN chmod +x install.sh

COPY . .

# train a new rasa model
# RUN rasa train nlu

# FROM postgres:14.1-alpine

# ENV POSTGRES_PASSWORD 7644
# ENV POSTGRES_DB Rasa

# set the user to run, don't run as root
USER 1001

# set entrypoint for interactive shells
ENTRYPOINT ["rasa"]

# command to run when container is called to run
CMD ["run", "--enable-api", "--port", "8080"] 