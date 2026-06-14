# ============================================================
# DataCo Web Scraper — Dockerfile
# ============================================================
# Builds a production-ready container image for the scraper.
#
# Build:  docker-compose build
# Run:    docker-compose run scraper full
# ============================================================

FROM python:3.12-slim

LABEL maintainer="DataCo Data Engineering"
LABEL description="Automated web scraping pipeline for DataCo"
LABEL version="1.0.0"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ── Install system dependencies ──────────────────────────────
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libxml2-dev \
        libxslt-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ── Copy project files and source code ───────────────────────
# Note: With editable installs (-e), setuptools needs the
# actual src/ directory to exist at install time to discover
# the package — so dependency installation and code copying
# cannot be fully separated for caching purposes here.
# This is a common and accepted tradeoff.
COPY pyproject.toml .
COPY src/ ./src/
COPY config/ ./config/

# ── Install dependencies ──────────────────────────────────────
RUN pip install --upgrade pip \
    && pip install -e "."

# ── Create runtime directories ───────────────────────────────
RUN mkdir -p data/raw data/processed logs

# ── Entry point ──────────────────────────────────────────────
ENTRYPOINT ["python", "-m", "src.dataco_web_scraper.pipeline"]

CMD ["full"]