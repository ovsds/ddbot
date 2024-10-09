FROM redis:7.4.1-alpine3.20

COPY redis.conf /usr/local/etc/redis/redis.conf
COPY users.acl /usr/local/etc/redis/users.acl
RUN chown -R redis:redis /usr/local/etc/redis

COPY entrypoint.sh /usr/local/bin/
ENTRYPOINT ["entrypoint.sh"]
