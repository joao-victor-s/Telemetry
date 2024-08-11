# Shared
FROM python:3.9 AS shared

ARG BUILD_ENV
ENV BUILD_ENV=${SECRET_KEY:-development} \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.0.0

# install poetry
RUN pip install "poetry==$POETRY_VERSION"

# install project dependencies first
WORKDIR /app
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false \
    && poetry install $(test "$BUILD_ENV" == production && echo "--no-dev") --no-interaction --no-ansi

# copy python files
COPY . .

# Metrics
FROM shared AS metrics
CMD ["python3", "-m", "metrics"]

# Event Hook
FROM shared AS eventhook
CMD ["python3", "-m", "eventhook"]

# Event Persister
FROM shared AS eventpersister
CMD ["python3", "-m", "eventpersister"]
