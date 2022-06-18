FROM alpine:20220328
RUN apk add \
        python3 \
        gcc \
        g++ \
        python3-dev \
        libxml2 \
        libxml2-dev \
        libxslt-dev \
        enchant2 \
        enchant2-dev && \
    python3 -m ensurepip

WORKDIR /home/taigabot
COPY ./requirements.txt ./requirements.txt
RUN python3 -m pip install -r requirements.txt
COPY ./requirements_extra.txt ./requirements_extra.txt
RUN python3 -m pip install -r requirements_extra.txt
COPY ./ ./

CMD [ "python3", "./bot.py" ]
