from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext, gettext_lazy as _
from alexa.models import Fact, FactType, User, Circle
from django.db import models
from utilities.widgets.split_json_widget import SplitJSONWidget
from jsonfield import JSONField


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('id',
                  'password',
                  'first_name',
                  'last_name',
                  'email',
                  'user_type',
                  'is_anonymous_user',
                  'date_joined',
                  'is_staff',
                  'is_active',
                  'user_type',
                  'senior_living_facility',
                  'phone_number', )

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    fieldsets = (
        (None, {'fields': ('email', 'password', 'user_type', 'device_serial', 'device_status', )}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone_number', )}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    list_display = ('id',
                    'first_name',
                    'last_name',
                    'email',
                    'user_type',
                    'device_status',
                    'date_joined',
                    'is_anonymous_user',
                    'is_staff',
                    'is_active',
                    'senior_living_facility',
                    'user_type',
                    'phone_number', )
    readonly_fields = ('id',
                       'profile_pic',
                       'date_joined',
                       'is_active',
                       'device_status',
                       'device_serial', )
    search_fields = ('first_name', 'last_name', 'email',)
    ordering = ('email',)
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_active', 'groups', )

    def device_serial(self, user: User):
        if not user.is_senior():
            return format_html("<span style='color: #aaa'>N/A</span>")
        qs = user.devices.all()
        if qs.count() == 0:
            return format_html("<span style='color: #888'>No Device</span>")
        device = qs[0]

        return format_html("<a href={}>{}</a>",
                           reverse('admin:senior_living_facility_seniordevice_change', args=(device.serial, )),
                           device.serial)

    def device_status(self, user: User):
        if not user.is_senior():
            return format_html("<span style='color: #aaa'>N/A</span>")
        qs = user.devices.all()
        if qs.count() == 0:
            return format_html("<span style='color: #888'>No Device</span>")
        device = qs[0]

        return format_html("<span style='color:{}; font-weight: bold; border:1px dashed #555; padding: 3px;'>{}</span>",
                           'green' if device.is_online else 'red',
                           'Online' if device.is_online else 'Offline', )


admin.site.register(User, UserAdmin)
admin.site.unregister(Group)


class CircleMembershipInlineAdmin(admin.TabularInline):
    model = Circle.members.through


# @admin.register(Circle)
class CircleAdmin(admin.ModelAdmin):
    fields = ('person_of_interest',
              )
    list_display = ('pk',
                    'person_of_interest',
                    )

    inlines = (CircleMembershipInlineAdmin, )

    readonly_fields = ('person_of_interest', )


# @admin.register(Fact)
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


# @admin.register(FactType)
class FactTypeAdmin(admin.ModelAdmin):
    pass
