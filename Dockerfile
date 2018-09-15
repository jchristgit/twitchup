FROM python:3.7-alpine

COPY . /app

RUN pip install --no-cache-dir praw==5.4.0

WORKDIR /config
ENTRYPOINT ["python", "/app/twitchup.py"]
