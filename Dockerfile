# pull official base image
FROM python:3.8.2 AS builder

ARG POSTGRES_DB
ARG POSTGRES_USER
ARG POSTGRES_PASSWORD

WORKDIR /usr/src/app

COPY . .

RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# install app to a temp folder
RUN pip install --upgrade pip && \
    pip install --no-cache-dir . && \
    pip install requests pytest pytest-asyncio

# run all tests
RUN DB_CONFIG_PATH=src/time_manager/.dbconfig.json pytest tests

RUN time_manager_admin generate_config \
    --db postgres \
    --name ${POSTGRES_DB} \
    --host db \
    --port 5432 \
    --username ${POSTGRES_USER} \
    --password ${POSTGRES_PASSWORD} \
    --output /tmp/.postgres.config.json


FROM python:3.8.2 AS service
WORKDIR /root/app/site-packages
COPY --from=builder /venv /venv
COPY --from=builder /tmp/.postgres.config.json /root/.postgres.config.json
ENV PATH=/venv/bin:$PATH
ENV DB_CONFIG_PATH=/root/.postgres.config.json
