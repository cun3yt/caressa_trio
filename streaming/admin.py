from django.contrib import admin
from streaming.models import AudioFile, Playlist, PlaylistHasAudio, HardwareRegistry
from alexa.models import AUser
from streaming.forms import AudioFileForm
from django.utils.html import format_html
from admin_ordering.admin import OrderableAdmin
from django_admin_relation_links import AdminChangeLinksMixin
from django.urls import reverse
from django.utils.safestring import mark_safe


@admin.register(AudioFile)
class AudioFileAdmin(admin.ModelAdmin):
    fields = ('audio_type',
              'duration',
              'name',
              'description',
              'url', )

    list_display = ('id',
                    'audio_type',
                    'url_hyperlink',
                    'duration',
                    'url_public_status',
                    'name',
                    'description', )

    readonly_fields = ('url_hyperlink',
                       'duration', )

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


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    fields = ('user',
              'name', )

    list_display = ('user',
                    'name', )


@admin.register(PlaylistHasAudio)
class PlaylistHasAudioAdmin(OrderableAdmin, AdminChangeLinksMixin, admin.ModelAdmin):
    ordering_field = 'order_id'     # this is for 'admin_ordering' package

    fields = ('playlist',
              'audio',
              'duration',
              'order_id', )

    list_display = ('id',
                    'playlist',
                    'audio_file',
                    'audio_file_external_link',
                    'duration',
                    'order_id', )

    list_editable = ('order_id', )

    list_filter = ('playlist', )

    filter = ('playlist', )

    search_fields = ('playlist__name',
                     'audio__name', )

    readonly_fields = ('duration', )

    change_links = ['audio']

    autocomplete_fields = ['audio', ]

    @staticmethod
    def audio_file(instance: PlaylistHasAudio):
        url = '<a href="{url}">{file_name}</a>'.format(url=reverse('admin:streaming_audiofile_change', args=(instance.audio.id,)),
                                                       file_name=instance.audio, )
        return mark_safe(url)

    @staticmethod
    def audio_file_external_link(instance: PlaylistHasAudio):
        url = '<a href="{url}" target="_blank">Listen</a>'.format(
            url=instance.audio.url, )
        return mark_safe(url)

    @staticmethod
    def duration(instance: PlaylistHasAudio):
        return instance.audio.duration_in_minutes


@admin.register(HardwareRegistry)
class HardwareRegistry(admin.ModelAdmin):
    fields = ('caressa_device_id',
              'device_id',
              'last_used_by',
              'notes', )

    list_display = ('id',
                    'caressa_device_id',
                    'list_device_id',
                    'last_used_by',
                    'notes', )

    readonly_fields = ('last_used_by', )

    def list_device_id(self, registry: HardwareRegistry):
        if len(registry.device_id) < 25:
            return registry.device_id
        return "{}...{}".format(registry.device_id[:10], registry.device_id[-15:])
    list_device_id.admin_order_field = 'device_id'

    @staticmethod
    def last_used_by(registry: HardwareRegistry):
        alexa_user_qs = AUser.objects.filter(alexa_device_id__exact=registry.device_id)
        if alexa_user_qs.count() < 1:
            return None
        return "{user} (AUser::{au_id}, User::{u_id})".format(
            user=alexa_user_qs[0].user,
            au_id=alexa_user_qs[0].id,
            u_id=alexa_user_qs[0].user.id, )