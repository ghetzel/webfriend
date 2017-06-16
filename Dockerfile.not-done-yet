FROM       debian:jessie-slim
MAINTAINER Gary Hetzel <garyhetzel@gmail.com>
ARG        DEBIAN_FRONTEND=noninteractive

RUN \
    apt-get update -qqy \
    && apt-get -qqy install \
        wget \
        ca-certificates \
        apt-transport-https \
        ttf-wqy-zenhei \
        ttf-unfonts-core \
        python2.7 \
        python2.7-dev \
        python-pip

RUN \
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb https://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update -qqy \
    && apt-get -qqy install google-chrome-stable \
    && rm /etc/apt/sources.list.d/google-chrome.list \
    && rm -rf \
        /var/lib/apt/lists/* \
        /var/cache/apt/*

RUN     mkdir /opt/webfriend
ADD     . /opt/webfriend
WORKDIR /opt/webfriend
RUN     pip install -e /opt/webfriend
