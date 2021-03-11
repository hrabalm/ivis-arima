#!/bin/bash
set -e

# wait for elasticsearch and mariadb to start
until nc -z -v -w30 mariadb 3306
do
    sleep 1
done

# run knex seed TODO: check environment for SEED?
(
    cd knex
    rm seeds/* # remove stocks seeds
    cp /seeds/* seeds/
    ../node_modules/.bin/knex migrate:latest # we have to run migrations before seed
    ../node_modules/.bin/knex seed:run
)

# start ivis server
cd /opt/ivis/server && sleep 1 && node index.js