from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.fields import AutoCreatedField


class CreatedTimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    ``created`` field.
    """
    created = AutoCreatedField(_('created'))

    class Meta:
        abstract = True
