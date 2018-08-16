from utilities.dictionaries import deep_get, deep_set
from django.db import models
from jsonfield import JSONField


class CacheMiss(Exception):
    pass


class CacheMixin(models.Model):
    class Meta:
        abstract = True

    cache = JSONField(default={})

    def invalidate_cache(self):
        self.cache = {}
        self.save()

    def get_cache_value(self, key):
        cache_miss_sequence = '~~~CACHE MISS~~~JD9218JD'

        val = deep_get(self.cache, 'data.{}'.format(key), cache_miss_sequence)
        if val == cache_miss_sequence:
            raise CacheMiss
        return val

    def set_cache_value(self, key, val):
        deep_set(self.cache, 'data.{}'.format(key), val)
        self.save()
