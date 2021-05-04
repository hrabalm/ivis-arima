FROM node:14-buster as base
RUN apt-get update && apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*
COPY ivis-core/server/package*.json /opt/demo/ivis-core/server/
COPY ivis-core/client/package*.json /opt/demo/ivis-core/client/
COPY ivis-core/shared/package*.json /opt/demo/ivis-core/shared/
WORKDIR /opt/demo/ivis-core
# use all cores during binary builds
ENV JOBS=max
RUN for nd in server client shared; do (cd $nd && npm i && npm cache clean --force); done


FROM base as dev
RUN npm install -g nodemon
COPY ./docker-entrypoint-dev.sh /docker-entrypoint.sh
ENTRYPOINT [ "/docker-entrypoint.sh" ]

# build client separately
FROM base as build-client
COPY ivis-core/client /opt/demo/ivis-core/client
COPY ivis-core/shared /opt/demo/ivis-core/shared
COPY ivis-core/locales /opt/demo/ivis-core/locales
WORKDIR /opt/demo/ivis-core/client
RUN cd /opt/demo/ivis-core/client && npm run build

FROM base as production
WORKDIR /opt/demo
COPY ivis-core/server /opt/demo/ivis-core/server
COPY ivis-core/shared /opt/demo/ivis-core/shared
COPY ivis-core/locales /opt/demo/ivis-core/locales
COPY server /opt/demo/server/
COPY lib /opt/demo/ivis-core/server/lib/tasks/python/ivis/
WORKDIR /opt/demo/ivis-core/server/lib/tasks/python/ivis
RUN python3 -m pip install --upgrade setuptools wheel && python3 setup.py sdist bdist_wheel
WORKDIR /opt/demo/ivis-core/
COPY --from=build-client /opt/demo/ivis-core/client /opt/demo/ivis-core/client
EXPOSE 8080 8081 8082
WORKDIR /opt/demo/ivis-core/server
COPY ./config/arima.yaml /opt/demo/ivis-core/server/config/arima.yaml
COPY ./docker-entrypoint.sh /
ENTRYPOINT [ "/docker-entrypoint.sh" ]

