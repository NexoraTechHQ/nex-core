FROM alpine:latest as main-linux-arm64
ARG PB_VERSION=0.17.7
RUN apk --no-cache add curl
RUN adduser -s /bin/bash -D pocketbase

USER pocketbase

WORKDIR /home/pocketbase
RUN curl -LJ "https://github.com/pocketbase/pocketbase/releases/download/v${PB_VERSION}/pocketbase_${PB_VERSION}_linux_arm64.zip" -o pb.zip
RUN unzip pb
RUN rm pb.zip

FROM alpine:latest as main-linux-armv7
ARG PB_VERSION=0.17.7
RUN apk --no-cache add curl
RUN adduser -s /bin/bash -D pocketbase

USER pocketbase

WORKDIR /home/pocketbase
RUN curl -LJ "https://github.com/pocketbase/pocketbase/releases/download/v${PB_VERSION}/pocketbase_${PB_VERSION}_linux_armv7.zip" -o pb.zip
RUN unzip pb
RUN rm pb.zip

FROM alpine:latest as main-linux-amd64
ARG PB_VERSION=0.26.6
RUN apk --no-cache add curl
RUN adduser -s /bin/bash -D pocketbase

USER pocketbase

WORKDIR /home/pocketbase
RUN curl -LJ "https://github.com/pocketbase/pocketbase/releases/download/v${PB_VERSION}/pocketbase_${PB_VERSION}_linux_amd64.zip" -o pb.zip
RUN unzip pb
RUN rm pb.zip

FROM main-${TARGETOS}-${TARGETARCH}${TARGETVARIANT}

ENV PRIVATE_POCKETBASE_ADMIN=""
ENV PRIVATE_POCKETBASE_PASSWORD=""
RUN mkdir pb_migrations
RUN mkdir pb_hooks
RUN mkdir pb_data && chown pocketbase:pocketbase pb_data

EXPOSE 8090
VOLUME [ "/home/pocketbase/pb_data" ]

COPY --chown=pocketbase --chmod=700 ./entrypoint.sh .

# Optional if you have local migrations or hooks
# COPY --chown=pocketbase --chmod=700 ./pb_migrations/ ./pb_migrations
# COPY --chown=pocketbase --chmod=700 ./pb_hooks/ ./pb_hooks
ENTRYPOINT [ "./entrypoint.sh" ]