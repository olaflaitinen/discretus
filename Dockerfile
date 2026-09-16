# Reproducible image for running and developing discretus.
FROM python:3.14-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY discretus ./discretus

RUN pip install --upgrade pip && pip install .

CMD ["python", "-c", "import discretus; print(discretus.__version__)"]


FROM base AS dev

COPY requirements-dev.txt constraints.txt ./
RUN pip install -r requirements-dev.txt

COPY . .

CMD ["python", "-m", "pytest", "tests"]
