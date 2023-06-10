FROM alpine:3.18 AS libs

RUN apk add libjpeg-turbo-dev libjpeg-turbo-utils
RUN apk add libwebp-dev libwebp-tools
RUN apk add libavif-dev libavif-apps
RUN apk add libjxl-dev libjxl-tools
RUN apk add libheif-dev libheif-tools

RUN apk add py3-pip dssim

WORKDIR /opt


FROM libs AS dev

RUN apk add perf htop

CMD echo 0 > /proc/sys/kernel/kptr_restrict && $0
