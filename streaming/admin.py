from django.contrib import admin
from streaming.models import AudioFile, Playlist, PlaylistHasAudio, UserPlaylistStatus, Tag
from streaming.forms import AudioFileForm
from django.utils.html import format_html
from admin_ordering.admin import OrderableAdmin
from django_admin_relation_links import AdminChangeLinksMixin
from django.urls import reverse
from django.utils.safestring import mark_safe
from utilities.time import seconds_to_minutes

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
            return format_html('<div style="width:100%%; height:100%%; background-color:red; color:white;">{}</div>'.format(
                obj.is_publicly_accessible()))
        return obj.is_publicly_accessible()

    url_public_status.allow_tags = True

    def audio_tags(self, obj):
        return [tag.name for tag in obj.tags.all()] if obj.tags.all().count() > 0 else \
            format_html('<div style="width:100%%; height:100%%; background-color:red; color:white;">No Tag Found</div>')



@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    change_list_template = 'playlist_changelist.html'
    fields = ('user',
              'name',
              'total_duration_in_minutes',
              'number_of_audio',
              )

    list_display = ('name',
                    'user',
                    'total_duration_in_minutes',
                    'number_of_audio', )

    readonly_fields = ('total_duration_in_minutes',
                       'number_of_audio', )

    @staticmethod
    def total_duration_in_minutes(instance: Playlist):
        return seconds_to_minutes(instance.total_duration) if instance.id else "--not set yet--"

    @staticmethod
    def number_of_audio(instance: Playlist):
        return instance.number_of_audio if instance.id else '--not set yet--'


@admin.register(PlaylistHasAudio)
class PlaylistHasAudioAdmin(OrderableAdmin, AdminChangeLinksMixin, admin.ModelAdmin):
    ordering_field = 'order_id'     # this is for 'admin_ordering' package

    fields = ('playlist',
              'audio',
              'tag',
              'duration',
              'order_id',
              'play_date',
              'play_time', )

    list_display = ('id',
                    'playlist',
                    'audio_file',
                    'audio_file_external_link',
                    'tag',
                    'duration',
                    'order_id',
                    'play_date',
                    'play_time',
                    'is_upcoming_content',
                    )

    list_editable = ('order_id',
                     'play_date',
                     'play_time', )

    list_filter = ('playlist', )

    filter = ('playlist', )

    search_fields = ('playlist__name',
                     'audio__name', )

    readonly_fields = ('duration', )

    change_links = ['audio']

    autocomplete_fields = ['audio', ]

    @staticmethod
    def audio_file(instance: PlaylistHasAudio):
        if not instance.audio:
            return 'tagged!'
        url = '<a href="{url}">{file_name}</a>'.format(url=reverse('admin:streaming_audiofile_change',
                                                                   args=(instance.audio.id,)),
                                                       file_name=instance.audio, )
        return mark_safe(url)

    def audio_file_external_link(self, instance: PlaylistHasAudio):
        if not instance.audio:
            return 'tagged!'
        url = '<a href="{url}" target="_blank">Listen</a>'.format(
            url=instance.audio.url, )
        return mark_safe(url)
    audio_file_external_link.short_description = 'Link'

    @staticmethod
    def duration(instance: PlaylistHasAudio):
        return instance.audio.duration_in_minutes if instance.audio else 'N/A'

    def is_upcoming_content(self, instance: PlaylistHasAudio):
        ups = UserPlaylistStatus.objects.all()
        if ups.filter(playlist_has_audio=instance.pk).count() > 0:
            return True
        else:
            return False
    is_upcoming_content.boolean = True
    is_upcoming_content.short_description = 'Next Audio'
