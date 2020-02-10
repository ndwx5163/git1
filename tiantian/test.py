import redis


client_redis=redis.StrictRedis(host="127.0.0.1",port=6379,db=0)

client_redis.flushdb()
client_redis.hmset("hash0",{"name":"xiaobai","age":18,"gender":"female","15":14})


result=client_redis.hdel("hash0",15)
print(result)

