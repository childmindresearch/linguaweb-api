FROM --platform=linux/amd64 public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

ENV LD_LIBRARY_PATH=/usr/lib:/usr/local/lib:/usr/local/lib64/:/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH}
ENV PYTHONPATH=${LAMBDA_TASK_ROOT}/src:${PYTHONPATH}

COPY pyproject.toml poetry.lock docker/aws/lambda.py ${LAMBDA_TASK_ROOT}
COPY src ${LAMBDA_TASK_ROOT}/src
COPY --from=jrottenberg/ffmpeg /usr/local /usr/local
COPY --from=jrottenberg/ffmpeg /lib/x86_64-linux-gnu/libssl.so.1.0.0 /lib/x86_64-linux-gnu/libcrypto.so.1.0.0 /lib/x86_64-linux-gnu/
COPY --from=jrottenberg/ffmpeg /usr/lib/x86_64-linux-gnu/libgomp.so.1 /usr/lib/x86_64-linux-gnu/libgomp.so.1.0.0 /usr/lib/

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --only=main --no-interaction --no-ansi && \
    rm -rf /root/.cache

CMD [ "lambda.handler" ]
