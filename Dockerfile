FROM python:3.12-slim AS base

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1
ENV ROOT=/src

WORKDIR $ROOT

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && apt-get install -y --no-install-recommends apt-utils \
    && apt-get install -y --no-install-recommends libc-dev \
    && apt-get install -y --no-install-recommends gcc \
    && apt-get install -y --no-install-recommends gettext \
    && apt-get install -y --no-install-recommends screen \
    && apt-get install -y --no-install-recommends vim \
    && apt-get install -y --no-install-recommends curl \
    && apt-get clean


ENV VIRTUALENV=$ROOT/venv
RUN python3 -m venv $VIRTUALENV
ENV PATH=$VIRTUALENV/bin:$PATH

COPY requirements.txt ./
COPY app/ $ROOT/app
COPY pyproject.toml ./


RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && playwright install --with-deps

FROM python:3.12-slim
ENV ROOT=/src

RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY --from=base $ROOT/venv $ROOT/venv
COPY --from=base /root/.cache/ms-playwright /root/.cache/ms-playwright
ENV PATH="$ROOT/venv/bin:$PATH"

RUN playwright install --with-deps chromium

COPY /app /app
WORKDIR /.

COPY start.sh ./
COPY logging_config.yaml ./
COPY pyproject.toml ./

RUN chmod +x ./start.sh
