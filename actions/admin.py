from django.contrib import admin
from actions.models import User, UserPost, ManualUserPost
from utilities.widgets.split_json_widget import SplitJSONWidget
from jsonfield import JSONField


@admin.register(UserPost)
class UserPostAdmin(admin.ModelAdmin):
    fields = ('user', 'data', )
    list_display = ('user', 'created', 'modified')

    formfield_overrides = {
        JSONField: {'widget': SplitJSONWidget(debug=False)},
    }


@admin.register(ManualUserPost)
class ManualUserPostAdmin(admin.ModelAdmin):
    fields = ('listened_time',
              'user',
              'content_to_be_spoken',
              'content_creation_time',
              'yes_no_question',
              'yes_reflection_on_circle',
              'is_published', )

    readonly_fields = ('listened_time', )

    list_display = ('user',
                    'content_to_be_spoken',
                    'yes_no_question',
                    'yes_reflection_on_circle',
                    'is_published',
                    'listened_time', )

    def has_change_permission(self, request, obj=None):
        # If an instance is listened already no change is allowed.
        if obj is not None and obj.listened_time is not None:
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        # If an instance is listened already no delete is allowed.
        if obj is not None and obj.listened_time is not None:
            return False
        return True
