import redis

r = redis.StrictRedis(host='10.10.4.252', port=6379, db=0)

p = r.lrange('chicago:ge-1/0/5:traffic statistics', 0, -1)[1]

print p