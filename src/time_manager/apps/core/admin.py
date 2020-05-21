from django.contrib import admin
from .models import Request, RequestType, Date, Comment
from django.utils.translation import ngettext
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django import forms
from django.db import models
from datetime import datetime

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    search_fields = ('comment',)

def convert_int_to_format(value, format):
    """ Converts an integer to a date string
    with the format.

    Parameters:
    value (int): value to convert
    format (str): time format

    Returns:
    string representation of a timestamp or an original value
    """

    if isinstance(value, int):
        return datetime.fromtimestamp(value).strftime(format)

    return value

class TimeFromIntegerInput(forms.widgets.TimeInput):
    """ Time input widget with the backing integer field,
    that represents the number of epoch timestamp (seconds).
    """

    def format_value(self, value):
        return super().format_value(convert_int_to_format(value, self.format))

    def get_context(self, name, value, attrs):
        return super().get_context(name, convert_int_to_format(value, self.format), attrs)

class TimeField(forms.IntegerField):
    format = '%H:%M'
    widget = TimeFromIntegerInput(format=format, attrs={'type': 'time'})
    def to_python(self, value):
        """Normalize data to an integer."""
        if not value:
            return 0

        pt = datetime.strptime(value, self.format)

        return pt.minute*60 + pt.hour*3600

    def validate(self, value):
        """Check if value consists only of valid emails."""
        super().validate(value)

class RequestForm(forms.ModelForm):
    end = TimeField(required=True)
    start = TimeField(required=True)

    class Meta:
        model = Request
        fields = '__all__'

@admin.register(Request)
class ShowDateAdmin(admin.ModelAdmin):
    form = RequestForm
    list_filter = ('user',)

@admin.register(Date)
class DateAdmin(admin.ModelAdmin):
    list_display = ('ts',)

class ReadOnlyMixin():

    actions = None

    enable_change_view = False

    def get_list_display_links(self, request, list_display):
        """
        Return a sequence containing the fields to be displayed as links
        on the changelist. The list_display parameter is the list of fields
        returned by get_list_display().

        Override Django's default implementation to specify no links unless
        they are explicitly set.
        """
        if self.list_display_links or not list_display:
            return self.list_display_links
        else:
            return (None,)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """
        The 'change' admin view for this model.

        Redirect back to the changelist unless the view is
        specifically enabled by the "enable_change_view" property.
        """
        if self.enable_change_view:
            return super().change_view(
                request,
                object_id,
                form_url,
                extra_context
            )
        else:
            opts = self.model._meta
            url = reverse(f'admin:{opts.app_label}_{opts.model_name}_changelist')
            return HttpResponseRedirect(url)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(RequestType)
class RTypeAdmin(ReadOnlyMixin, admin.ModelAdmin):
    pass
