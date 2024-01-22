FROM --platform=linux/amd64 public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

ENV LD_LIBRARY_PATH=/usr/local/lib:/usr/local/lib64/:/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH}

COPY pyproject.toml poetry.lock ${LAMBDA_TASK_ROOT}
COPY src ${LAMBDA_TASK_ROOT}/src
COPY --from=jrottenberg/ffmpeg /usr/local /usr/local
COPY --from=jrottenberg/ffmpeg /lib/x86_64-linux-gnu/libssl.so.1.0.0 /lib/x86_64-linux-gnu/

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi && \
    rm -rf /root/.cache

CMD [ "src/linguaweb_api/main.handler" ]
