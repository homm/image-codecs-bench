FROM alpine:3.18 AS libs

RUN apk add libjpeg-turbo-dev libjpeg-turbo-utils
RUN apk add libwebp-dev libwebp-tools
RUN apk add libavif-dev libavif-apps
RUN apk add libjxl-dev libjxl-tools
RUN apk add libheif-dev libheif-tools

RUN apk add py3-pip dssim

WORKDIR /opt


FROM libs AS ssimulacra2

RUN apk add g++ cmake
RUN apk add libpng-dev samurai

ADD ssimulacra2 .

RUN mkdir build && cd build \
  && cmake ../src -DCMAKE_CXX_FLAGS="-g1" -DCMAKE_BUILD_TYPE=Release -G Ninja \
  && ninja ssimulacra2


FROM libs AS dev

RUN apk add perf htop

COPY --from=ssimulacra2 /opt/build/ssimulacra2 /usr/bin/ssimulacra2

CMD echo 0 > /proc/sys/kernel/kptr_restrict && $0
