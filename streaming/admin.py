from django.contrib import admin
from streaming.models import AudioFile, Tag
from streaming.forms import AudioFileForm
from django.utils.html import format_html

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    fields = ('name',
              'label',
              'is_setting_available', )

    list_display = ('id',
                    'name',
                    'label',
                    'is_setting_available', )


@admin.register(AudioFile)
class AudioFileAdmin(admin.ModelAdmin):
    fields = ('audio_type',
              'duration_in_minutes',
              'name',
              'description',
              'url',
              'tags', )

    list_display = ('id',
                    'audio_type',
                    'url_hyperlink',
                    'duration_in_minutes',
                    'url_public_status',
                    'name',
                    'description',
                    'audio_tags', )

    readonly_fields = ('url_hyperlink',
                       'duration_in_minutes', )

    ordering = ['-modified', ]

    search_fields = ['name', ]

    form = AudioFileForm

    def get_fields(self, request, obj=None):
        if obj:
            return self.fields + ('url_hyperlink', )
        return self.fields

    def url_public_status(self, obj):
        if not obj.is_publicly_accessible():
            return format_html('<div '
                               'style="width:100%%; '
                               'height:100%%; '
                               'background-color:red; '
                               'color:white;">{}</div>'.format(obj.is_publicly_accessible()))
        return obj.is_publicly_accessible()

    url_public_status.allow_tags = True

    def audio_tags(self, obj):
        return [tag.name for tag in obj.tags.all()] if obj.tags.all().count() > 0 else \
            format_html('<div style="width:100%%; height:100%%; background-color:red; color:white;">No Tag Found</div>')


