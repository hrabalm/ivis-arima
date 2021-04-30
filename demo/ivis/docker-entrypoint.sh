#!/bin/bash
set -e

# wait for elasticsearch and mariadb to start
until nc -z -v -w30 elasticsearch 9200
do
    sleep 1
done

until nc -z -v -w30 mariadb 3306
do
    sleep 1
done

# start ivis server
cd /opt/demo/server && node index.js
