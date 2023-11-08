FROM python:3.11-bullseye

EXPOSE 8000

WORKDIR /app

COPY pyproject.toml poetry.lock ./
COPY src ./src

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi && \
    rm -rf /root/.cache

CMD ["poetry", "run", "uvicorn", "linguaweb_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "src"]
