FROM python:3.9-buster

ENV LC_ALL=C.UTF-8 LANG=C.UTF-8 PIP_NO_CACHE_DIR=false

RUN DEBIAN_FRONTEND=noninteractive \
    apt-get update &&\
    apt-get install -y --no-install-recommends libpcre3-dev libpq-dev build-essential git ffmpeg &&\
    apt-get clean &&\
    rm -rf /var/lib/apt/lists/*
RUN pip3 install --upgrade poetry~=1.1.8 && \
    poetry config virtualenvs.in-project true

WORKDIR /srv/backend

# Add dependencies and install them
COPY pyproject.toml poetry.lock /srv/backend/
RUN poetry install --no-dev -v

# Copy source
COPY . /srv/backend/

# Required build-time arguments
ARG REDIS_MAIN_INSTANCE="redis://127.0.0.1:6379"
ARG TELEGRAM_TOKEN=""
ARG DATABASE_URL="sqlite://:memory:"
ARG SECRET_KEY="0"

# Build assets
RUN poetry run python manage.py collectstatic --noinput --verbosity 0

EXPOSE 8080

LABEL org.opencontainers.image.source=https://github.com/gamepad64/libupd8
