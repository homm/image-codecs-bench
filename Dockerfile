FROM alpine:3.18

RUN apk add libjpeg-turbo-dev libjpeg-turbo-utils
RUN apk add libwebp-dev libwebp-tools
RUN apk add libavif-dev libavif-apps
RUN apk add libjxl-dev libjxl-tools

RUN apk add py3-pip dssim

WORKDIR /opt
