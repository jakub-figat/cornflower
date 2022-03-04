FROM python:3.9.5-slim-buster


ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_VERSION=1.1.13 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry'

WORKDIR /app

COPY pyproject.toml poetry.lock poetry.toml ./

RUN pip install poetry=="$POETRY_VERSION"

RUN poetry install

COPY . .


ENTRYPOINT ["python", "example.py"]
EXPOSE 8000