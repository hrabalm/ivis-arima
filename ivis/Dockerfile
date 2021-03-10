FROM node:14-alpine

RUN apk add --update python python3 make gcc g++ git bash
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools


COPY ivis-core/server/package.json /opt/ivis/server/package.json
COPY ivis-core/server/package-lock.json /opt/ivis/server/package-lock.json

COPY ivis-core/client/package.json /opt/ivis/client/package.json
COPY ivis-core/client/package-lock.json /opt/ivis/client/package-lock.json

COPY ivis-core/shared/package.json /opt/ivis/shared/package.json
COPY ivis-core/shared/package-lock.json /opt/ivis/shared/package-lock.json

WORKDIR /opt/ivis/

RUN for nd in server client shared; do (cd $nd && npm ci); done

WORKDIR /opt/ivis/

COPY ivis-core /opt/ivis

# TODO: Install ivis library for Python
WORKDIR /opt/ivis/server/lib/tasks/python/ivis
RUN python3 -m pip install --upgrade setuptools wheel && python3 setup.py sdist bdist_wheel

WORKDIR /opt/ivis/

RUN cd client && npm run build

EXPOSE 8080 8081 8082

WORKDIR /opt/ivis/server

COPY arima.yaml /opt/ivis/server/config/arima.yaml
#CMD [ "node", "index.js" ]
