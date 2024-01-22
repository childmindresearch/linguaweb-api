FROM python:3.12-bullseye

EXPOSE 8000

WORKDIR /app

COPY pyproject.toml poetry.lock ./
COPY src ./src

RUN apt-get update && \
    apt-get install -y ffmpeg && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi && \
    rm -rf /root/.cache

CMD ["poetry", "run", "uvicorn", "linguaweb_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "src"]
