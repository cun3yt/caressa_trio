from django.contrib import admin
from alexa.models import Fact, FactType
# from django.db import models
from django import forms
from utilities.widgets.split_json_widget import SplitJSONWidget
from jsonfield import JSONField


@admin.register(Fact)
class FactAdmin(admin.ModelAdmin):
    def upper_case_entry_text(self, obj):
        return obj.entry_text.upper()

    upper_case_entry_text.short_description = 'Entry Text Ho'
    upper_case_entry_text.admin_order_field = 'entry_text'

    fields = ('fact_type', 'entry_text', 'fact_list', 'ending_yes_no_question', )
    list_display = ('fact_type', 'entry_text', 'upper_case_entry_text', )

    formfield_overrides = {
        JSONField: {'widget': SplitJSONWidget(debug=False)}
    }


@admin.register(FactType)
class FactTypeAdmin(admin.ModelAdmin):
    pass
