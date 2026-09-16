# Reproducible image for running and developing discretus.
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

LABEL org.opencontainers.image.title="discretus" \
      org.opencontainers.image.description="A rigorous, production-grade library for Discrete Mathematics in pure Python." \
      org.opencontainers.image.version="discretus:1.0.0" \
      org.opencontainers.image.authors="Olaf Yunus Laitinen Imanov <yimanov@student.uef.fi>" \
      org.opencontainers.image.url="https://github.com/olaflaitinen/discretus" \
      org.opencontainers.image.documentation="https://discretus.readthedocs.io" \
      org.opencontainers.image.source="https://github.com/olaflaitinen/discretus" \
      org.opencontainers.image.licenses="MPL-2.0" \
      org.opencontainers.image.base.name="docker.io/library/python:3.12-slim"

WORKDIR /app

COPY pyproject.toml README.md LICENSE NOTICE ./
COPY discretus ./discretus

RUN pip install --upgrade pip && pip install .

CMD ["python", "-c", "import discretus; print(discretus.__version__)"]


FROM base AS dev

COPY requirements-dev.txt constraints.txt ./
RUN pip install -r requirements-dev.txt

COPY . .

CMD ["python", "-m", "pytest", "tests"]
