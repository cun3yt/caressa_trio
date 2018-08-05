from django.contrib import admin
from alexa.models import Fact, FactType, User, Circle
from django.db import models
from django import forms
from utilities.widgets.split_json_widget import SplitJSONWidget
from jsonfield import JSONField


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fields = ('username',
              'first_name',
              'last_name',
              'email',
              'date_joined',
              'is_staff',
              'is_active',
              'user_type',
              'phone_number',
              'profile_pic', )
    list_display = ('username',
                    'first_name',
                    'last_name',
                    'email',
                    'date_joined',
                    'is_staff',
                    'is_active',
                    'user_type',
                    'phone_number', )
    readonly_fields = ('profile_pic',
                       'date_joined',
                       'is_active', )


class CircleMembershipInlineAdmin(admin.TabularInline):
    model = Circle.members.through


@admin.register(Circle)
class CircleAdmin(admin.ModelAdmin):
    fields = ('person_of_interest',
              )
    list_display = ('pk',
                    'person_of_interest',
                    )

    inlines = (CircleMembershipInlineAdmin, )

    readonly_fields = ('person_of_interest', )


@admin.register(Fact)
class FactAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('css/admin.css', )
        }
        js = ('js/admin.js', )

    fields = ('fact_type', 'entry_text', 'fact_list', 'ending_yes_no_question', )
    list_display = ('fact_type', 'entry_text', )

    formfield_overrides = {
        JSONField: {'widget': SplitJSONWidget(debug=False)},
        models.TextField: {'widget': forms.TextInput(attrs={'style': 'width:70%'})},
    }


@admin.register(FactType)
class FactTypeAdmin(admin.ModelAdmin):
    pass
