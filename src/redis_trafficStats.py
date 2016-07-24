import redis

r = redis.StrictRedis(host='10.10.4.252', port=6379, db=0)


# Saves the traffic statistics of a certain node's interface
# <VARIABLE> = r.lrange('<NODE NAME>:ge-<INTERFACE ID>:traffic statistics', 0, -1)[1]
a = r.lrange('chicago:ge-1/0/5:traffic statistics', 0, -1)[1]
b = r.lrange('chicago:ge-1/0/4:traffic statistics', 0, -1)[1]
c = r.lrange('chicago:ge-1/0/2:traffic statistics', 0, -1)[1]

print "chicago:ge-1/0/5:"
print a ,"\n"
print "chicago:ge-1/0/4:"
print b ,"\n"
print "chicago:ge-1/0/2:"
print c ,"\n"