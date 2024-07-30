docker-compose: build-image
    op run --env-file=.env-dev -- docker compose up    

build-image:
    docker build -t hhollenstain/autochannel-bot:latest .
