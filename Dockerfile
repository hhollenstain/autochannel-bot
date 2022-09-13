FROM python:3.6-alpine

RUN apk add gcc musl-dev libffi-dev libxml2-dev libxslt-dev git make postgresql-dev

COPY . /app
WORKDIR /app

RUN make live

CMD ["autochannel"]
