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

# run knex seed not yet done
(
    if [ -e /seeded ]
    then
        echo "Skipping knex seeds and migrations as they have already been run."
    else
        cd knex
        rm seeds/* # remove stock seeds
        cp /seeds/* seeds/
        ../node_modules/.bin/knex migrate:latest # we have to run migrations before seed
        ../node_modules/.bin/knex seed:run
        touch /seeded
    fi
)

if [ $NODE_WATCH ]
then
    (
        cd /opt/demo/ivis-core/client
        npm run watch
    ) &
fi

# start ivis server
cd /opt/demo/server && sleep 1 && node index.js
