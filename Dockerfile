FROM python:3.14-alpine

RUN apk add gcc g++ musl-dev libffi-dev libxml2-dev libxslt-dev git make postgresql-dev
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY . /app
WORKDIR /app

RUN uv pip install --system -e .

CMD ["autochannel"]
