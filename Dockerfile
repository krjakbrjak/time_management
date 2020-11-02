# pull official base image
FROM python:3.8.2 AS builder

WORKDIR /usr/src/app

RUN pip install --upgrade pip
COPY . .
RUN pip install -r requirements.txt

# Check code with linters
RUN isort -c --profile black src/ && \
    black --check src/ && \
    flake8 src/ && \
    MYPYPATH=src mypy --namespace-packages -p time_manager && \
    isort -c --profile black tests/ && \
    black --check tests/ && \
    flake8 tests/ && \
    MYPYPATH=src mypy --namespace-packages tests

# install app to a temp folder
RUN pip install . --target=TIME_MANAGER_APP

# Run tests
RUN PYTHONPATH=TIME_MANAGER_APP DB_URL=sqlite:////tmp/tmp.db pytest tests

# Run migrations
RUN PYTHONPATH=TIME_MANAGER_APP alembic upgrade heads


FROM python:3.8.2-alpine AS service
RUN apk --no-cache add ca-certificates
WORKDIR /root/app/site-packages
COPY --from=builder /usr/src/app/TIME_MANAGER_APP .
