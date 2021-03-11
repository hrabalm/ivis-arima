FROM node:14-buster

RUN apt-get update && apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY ivis-core/server/package*.json /opt/ivis/server/
COPY ivis-core/client/package*.json /opt/ivis/client/
COPY ivis-core/shared/package*.json /opt/ivis/shared/

WORKDIR /opt/ivis/

# use all cores during binary builds
ENV JOBS=max
RUN for nd in server client shared; do (cd $nd && npm ci); done

WORKDIR /opt/ivis/

COPY ivis-core /opt/ivis

WORKDIR /opt/ivis/server/lib/tasks/python/ivis
RUN python3 -m pip install --upgrade setuptools wheel && python3 setup.py sdist bdist_wheel

WORKDIR /opt/ivis/

RUN cd client && npm run build

EXPOSE 8080 8081 8082

WORKDIR /opt/ivis/server

COPY arima.yaml /opt/ivis/server/config/arima.yaml

COPY ./docker-entrypoint.sh /

COPY ./seeds/ /seeds

ENTRYPOINT [ "/docker-entrypoint.sh" ]