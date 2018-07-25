from django.contrib import admin
from alexa.models import Fact, FactType
from django.db import models
from django import forms
from utilities.widgets.split_json_widget import SplitJSONWidget
from jsonfield import JSONField


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
