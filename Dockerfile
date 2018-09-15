FROM python:3.7-alpine

COPY . /app

RUN pip install --no-cache-dir praw==5.4.0

WORKDIR /config
CMD ["python", "/app/twitchup.py"]
