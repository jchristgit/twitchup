FROM python:3.7-alpine

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /config
ENTRYPOINT ["python", "/app/twitchup.py"]
