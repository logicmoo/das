#!/bin/bash

docker stop mongo >& /dev/null
docker rm mongo >& /dev/null
docker run \
    --detach \
    --env MONGO_INITDB_ROOT_USERNAME=${DAS_DATABASE_USERNAME:-dbadmin} \
    --env MONGO_INITDB_ROOT_PASSWORD=${DAS_DATABASE_PASSWORD:-dassecret} \
    --env TZ=${TZ} \
    --network="host" \
    --volume /tmp:/tmp \
    --volume /mnt:/mnt \
    --volume mongodbdata:/data/db \
    mongo:latest \
    mongod --port ${DAS_MONGODB_PORT:-27017}
