FROM rasa/rasa:2.8.2-full

WORKDIR '/app'

COPY . /app

USER root

COPY ./data /app/data

RUN rasa train

VOLUME /app

VOLUME /app/data

VOLUME /app/models

# CMD ["run","-m","/app/models","--enable-api", "--port", "8080", "--endpoints", "endpoints.yml", "--credentials",  "credentials.yml"]
# CMD ["run", "--endpoints", "endpoints.yml", "--credentials",  "credentials.yml"]
# CMD ["run"]