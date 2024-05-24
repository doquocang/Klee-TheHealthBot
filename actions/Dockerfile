FROM rasa/rasa-sdk:2.8.6

WORKDIR /app

COPY requirements-actions.txt requirements-actions.txt

USER root

RUN pip install --verbose -r requirements-actions.txt

EXPOSE 5055

USER 1001

# FROM python:3.8-slim
#
# RUN python -m pip install rasa==2.8.2
#
# WORKDIR /APP
# COPY . .
#
# RUN rasa train
#
# USER 1001
#
# ENTRYPOINT ["rasa"]
#
# EXPOSE 8080
#
# EXPOSE 5055
#
# EXPOSE 5050
#
# CMD ["run", "--enable-api", "--port", "8080"]
# CMD ["run", "actions]
