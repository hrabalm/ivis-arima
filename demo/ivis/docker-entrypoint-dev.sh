#!/bin/bash
set -e

(
    cd /opt/demo/ivis-core/server/lib/tasks/python/ivis
    python3 -m pip install --upgrade setuptools wheel && python3 setup.py sdist bdist_wheel
)

# wait for elasticsearch and mariadb to start
until nc -z -v -w30 elasticsearch 9200
do
    sleep 1
done

until nc -z -v -w30 mariadb 3306
do
    sleep 1
done

(
    cd /opt/demo/ivis-core/
    for d in client server shared
    do
        (
            cd "$d"
            if [ ! -d node_modules ]
            then
                npm ci
            fi
        )
    done
)

# start ivis server
cd /opt/demo/server && nodemon index.js
