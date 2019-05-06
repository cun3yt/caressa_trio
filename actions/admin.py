from django.contrib import admin
from actions.models import ActionGeneric


@admin.register(ActionGeneric)
class ActionGenericAdmin(admin.ModelAdmin):
    fields = ('id',
              'to_user',
              'data',
              'created',
              'modified', )
    list_display = ('id',
                    'to_user',
                    'created',
                    'modified', )
    readonly_fields = ('id',
                       'created',
                       'modified', )
