FROM python:3-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_ROOT_USER_ACTION ignore
WORKDIR /app
COPY . /app

RUN pip install --no-cache --upgrade pip \
 && pip install --no-cache /app \
 && addgroup --system app && adduser --system --group app \
 && mkdir -p /tmp/ca-pwt \
 && chown -R app:app /tmp/ca-pwt

USER app

VOLUME /tmp/ca-pwt

ENTRYPOINT ["ca-pwt"]
