import redis
import pickle
from copy import deepcopy
from typing import Any

from app.core.project_config import settings

class Cache:

    model_mapping = {}
    function_mapping = {}

    def __init__(self):
        try:
            self.__redis = redis.Redis(host='localhost', port=settings.REDIS_PORT)
            self.__redis.config_set("maxmemory", settings.REDIS_MAXMEMORY)
            self.__redis.config_set("maxmemory-policy", settings.REDIS_POLICY)
            self.__redis.config_set("stop-writes-on-bgsave-error", "no")
            self.__time_to_live = settings.REDIS_TIME_TO_LIVE
        except:
            pass
        
    def set(self, key: Any, value: Any):
        try:    
            data = pickle.dumps(value)
            self.__redis.setex(key, self.__time_to_live, data)
        except:
            pass

    def get(self, key: str):
        try:
            return pickle.loads(self.__redis.get(key))
        except:
            raise Exception()

    def append(self, key: Any, value: Any):
        try:
            self.__redis.append(key, value)
        except:
            self.set(key, value)
    
    def remove(self, key: Any):
        try:
            self.__redis.delete(key)
        except:
            pass

    async def update(self, service_self: Any, model: str):
        try:
            for function in Cache.model_mapping[model]:
                for params in Cache.function_mapping[function.__name__]:
                    args, kargs = params
                    res = await function(service_self, *deepcopy(args), **deepcopy(kargs))
                    key = str(function.__name__) + str(args) + str(kargs)
                    self.set(key, res)
        except:
            pass

    def delete(self, model: str):
        try:
            for function in Cache.model_mapping[model]:
                for params in Cache.function_mapping[function.__name__]:
                    args, kargs = params
                    key = str(function.__name__) + str(args) + str(kargs)
                    self.remove(key)
                Cache.function_mapping.pop(function.__name__)
            Cache.model_mapping.pop(model)
        except:
            pass

    def is_exist(self, key: Any):
        return self.__redis.exists(key)

    def get_keys(self):
        return self.__redis.keys()

    def clear(self):
        try:
            self.__redis.flushdb()
        except:
            pass

    def get_current_memory(self):
        return self.__redis.info()['used_memory']

    def get_info(self):
        return self.__redis.info()

    @staticmethod
    def set_model_mapping(model, function):
        if model not in Cache.model_mapping.keys():
            Cache.model_mapping[model] = [function]
        elif function not in Cache.model_mapping[model]:
            Cache.model_mapping[model].append(function)
        Cache.function_mapping[function.__name__] = []

    @staticmethod
    def set_function_mapping(function, params):
        if function not in Cache.function_mapping.keys():
            Cache.function_mapping[function] = [params]
        elif params not in Cache.function_mapping[function]:
            Cache.function_mapping[function].append(params)

__cache = Cache()
__cache.clear()

def cache(*_args, **_kargs):
    def decorator(function):
        async def wrapper(self: Any = None, *args, **kargs):
            Cache.set_model_mapping(model=self.__class__.__name__, function=function)
            Cache.set_function_mapping(function=function.__name__, params=(args, kargs))
            key = str(function.__name__) + str(args) + str(kargs)
            try:
                res = __cache.get(key)
            except:
                res = await function(self, *deepcopy(args), **deepcopy(kargs))
                __cache.set(key, res)
            return res
        return wrapper
    return decorator

def cache_update(*_args, **_kargs):
    def decorator(function):
        async def wrapper(self, *args, **kargs):
            res = await function(self, *args, **kargs)
            await __cache.update(service_self=self, model=self.__class__.__name__)
            return res
        return wrapper
    return decorator

def cache_delete(*_args, **_kargs):
    def decorator(function):
        async def wrapper(self, *args, **kargs):
            res = await function(self, *args, **kargs)
            __cache.delete(model=self.__class__.__name__)
            return res
        return wrapper
    return decorator