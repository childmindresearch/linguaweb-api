# LinguaWeb API

[![Build](https://github.com/childmindresearch/linguaweb-api/actions/workflows/test.yaml/badge.svg?branch=main)](https://github.com/childmindresearch/linguaweb-api/actions/workflows/test.yaml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/childmindresearch/linguaweb-api/branch/main/graph/badge.svg?token=22HWWFWPW5)](https://codecov.io/gh/childmindresearch/linguaweb-api)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![stability-wip](https://img.shields.io/badge/stability-work_in_progress-lightgrey.svg)

Welcome to the LinguaWeb API repository, an API for the LinguaWeb website. This API is built using [FastAPI](https://fastapi.tiangolo.com/), a modern, high-performance web framework for building APIs.

## What is a FastAPI Server?

FastAPI is a high-performance web framework for building APIs with Python 3.6+ based on standard Python type hints. It's known for its speed, ease of use, and automatic generation of OpenAPI documentation. This makes it ideal for building robust, scalable, and well-documented web applications and services.

## Getting Started

### Installation and Running with Poetry

1. Install Poetry, a dependency management tool, if you haven't already.
2. Clone the repository and navigate to the project directory.
3. Install dependencies using Poetry:

```bash
poetry install
```

4. Start the FastAPI server:

```bash
poetry run uvicorn linguaweb_api.main:app --port 8000 --app-dir src --env-file .env.example --reload
```

### Using Docker

Alternatively, use Docker to build and run the application in an isolated environment.

1. Run the Docker container from the GitHub repository:

```bash
docker run -p 8000:8000 ghcr.io/childmindresearch/linguaweb-api:main
```

## Accessing the OpenAPI Specification

The FastAPI server automatically generates and serves an OpenAPI specification for the API. Once the server is running, access the interactive API documentation at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

These pages provide a detailed overview of all available API endpoints, their expected input parameters, and response formats.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests.
