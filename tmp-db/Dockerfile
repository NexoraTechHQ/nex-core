FROM alpine:latest as main-linux-amd64
ARG PB_VERSION=0.26.6
RUN apk --no-cache add curl
RUN adduser -s /bin/bash -D pocketbase

USER pocketbase

WORKDIR /home/pocketbase
RUN curl -LJ "https://github.com/pocketbase/pocketbase/releases/download/v${PB_VERSION}/pocketbase_${PB_VERSION}_linux_amd64.zip" -o pb.zip
RUN unzip pb.zip
RUN rm pb.zip

FROM main-linux-amd64

ENV PRIVATE_POCKETBASE_ADMIN=""
ENV PRIVATE_POCKETBASE_PASSWORD=""
RUN mkdir pb_migrations
RUN mkdir pb_hooks
RUN mkdir pb_data && chown pocketbase:pocketbase pb_data

EXPOSE 8090
VOLUME [ "/home/pocketbase/pb_data" ]

# Copy the entrypoint.sh script directly without chmod
COPY ./entrypoint.sh /home/pocketbase/entrypoint.sh

ENTRYPOINT [ "/bin/sh", "/home/pocketbase/entrypoint.sh" ]
