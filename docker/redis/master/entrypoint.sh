#!/usr/bin/env sh
set -e

sed -i "s/\$REDIS_PASSWORD/$REDIS_PASSWORD/g" /usr/local/etc/redis/users.acl

exec docker-entrypoint.sh "$@"
