FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV APP_HOME=/app
RUN mkdir $APP_HOME

RUN apt update -y
RUN apt install build-essential libssl-dev libffi-dev libpq-dev libmagic1 libcairo2 -y
RUN apt install -y cron && rm -rf /var/lib/apt/lists/*

WORKDIR $APP_HOME

COPY poetry.lock .
COPY pyproject.toml .

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-root

COPY . $APP_HOME

COPY crontab /etc/cron.d/parsalov-cron
RUN chmod 0644 /etc/cron.d/parsalov-cron
RUN crontab /etc/cron.d/parsalov-cron

CMD ["cron", "-f"]
