import redis


class RedisClient():
    def __init__(self):
        self.red = redis.StrictRedis(host='54.223.140.206', port=6379, db=0)

    def saveValue(self, key, value):
        result = self.red.set(str(key), value)
        if result:
            return True
        return result

    def getValue(self, key):
        result = self.red.get(str(key))
        return result

    def delValue(self, key):
        result = self.red.delete(str(key))
        return result

    def getRangeValue(self, key, start, end):
        result = self.red.getrange(key, start, end)
        return result

    def getRedisInfo(self):
        result = self.red.info()
        return result

    def appendValue(self, key, value):
        result = self.red.append(key, value)
        return result

    def getKeySize(self, key):
        result = self.red.llen(key)
        return result
