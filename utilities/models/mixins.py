from django.contrib.auth import get_user_model

from caressa.settings import S3_REGION, S3_PRODUCTION_BUCKET
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


class ProfilePictureMixin:
    def get_profile_picture_url(self, dimensions, file_format):
        user = get_user_model()
        upper_dir = self.id if self.profile_pic else 'no_user'
        profile_picture = self.profile_pic if self.profile_pic else 'default_profile_pic'
        picture_owner_type = 'user' if isinstance(self, user) else 'facility'
        format_string = '{region}/{bucket}/images/{picture_owner_type}/{upper_dir}/{profile_picture}_{dimensions}.{file_format}'
        return format_string.format(region=S3_REGION,
                                    bucket=S3_PRODUCTION_BUCKET,
                                    profile_picture=profile_picture,
                                    picture_owner_type=picture_owner_type,
                                    upper_dir=upper_dir,
                                    dimensions=dimensions,
                                    file_format=file_format)

    def get_profile_pic(self):
        return self.get_profile_picture_url('w_250', 'jpg')

    def get_profile_pictures(self):
        return {
            'w_250': self.get_profile_picture_url('w_250', 'jpg'),
            'w_25': self.get_profile_picture_url('w_25', 'jpg'),
            'raw': self.get_profile_picture_url('raw', 'png'),
        }
