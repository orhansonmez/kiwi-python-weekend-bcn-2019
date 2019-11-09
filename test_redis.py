from redis import StrictRedis
import json

redis = StrictRedis(socket_connect_timeout=3, **{'host': '34.77.218.145','port': 80})

connections = json.loads(redis.get('bcn_orhan:journey:barcelona_madrid_2019-11-10'))

print(connections)