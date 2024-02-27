FROM python:latest


WORKDIR /application

COPY ./clubhub .


ENV FLASK_APP="src/main.py"
ENV FLASK_RUN_HOST="0.0.0.0"
ARG DATABASE_URL
EXPOSE 5000

RUN ["pip", "install", "-r", "requirements.txt"]

CMD ["flask", "run"]
