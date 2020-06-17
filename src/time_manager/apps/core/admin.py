from django.contrib import admin
from .models import TimeRequest, RequestType, Comment
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

@admin.register(TimeRequest)
class ShowDateAdmin(admin.ModelAdmin):
    list_filter = ('user', 'start')

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
