# coding: utf-8
import datetime
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.forms import ModelForm
from django.template.defaultfilters import truncatechars
from django.utils.html import linebreaks
from django.utils.safestring import mark_safe
from httplog.models import Entry


class EntryForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(EntryForm, self).__init__(*args, **kwargs)
        self.instance.in_headers = mark_safe(linebreaks(self.instance.in_headers))
        self.instance.out_headers = mark_safe(linebreaks(self.instance.in_headers))

    class Meta:
        model = Entry


class UserFilter(SimpleListFilter):
    title = 'user'
    parameter_name = 'user'

    def lookups(self, request, model_admin):
        users = set([log.user for log in model_admin.model.objects.all()])
        return [(user.pk, user.username) for user in users if user]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user_id__exact=self.value())
        else:
            return queryset


class CreatedFilter(SimpleListFilter):
    title = 'Time'
    parameter_name = 'created'

    def lookups(self, request, model_admin):

        def total_seconds(td):
            # 2.6 backport
            return int((td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6)

        return [(total_seconds(datetime.timedelta(**time_item[1])), time_item[0]) for time_item in (
            ('24 hours', {'hours': 24}),
            ('12 hours', {'hours': 12}),
            ('6 hours', {'hours': 6}),
            ('1 hour', {'hours': 1}),
            ('15 minutes', {'minutes': 15}),
        )]

    def queryset(self, request, queryset):
        if self.value():
            timestamp = datetime.datetime.now() - datetime.timedelta(seconds=int(self.value()))
            return queryset.filter(created__gt=timestamp)
        else:
            return queryset


class LogAdmin(admin.ModelAdmin):
    form = EntryForm
    list_display = ('short_url', 'method', 'status_code', 'user', 'ip', 'app_name', 'created')
    list_filter = ('app_name', 'status_code', 'method', UserFilter, CreatedFilter)
    search_fields = ('url', 'ip')
    date_hierarchy = 'created'
    fieldsets = (
        (u'Main', {'fields': ('url', 'method', 'status_code')}),
        (u'Request', {'fields': ('request', 'data', 'response')}),
        (u'System', {'fields': ('ip', 'app_name', 'user')}),
        (u'Headers', {'fields': ('in_headers', 'out_headers')}),
    )

    def get_readonly_fields(self, request, obj=None):
        """Make all readonly, cause it's a log"""
        return [field.name for field in self.opts.local_fields]

    def short_url(self, obj):
        return truncatechars(obj.url, 30)
    short_url.short_description = 'URL'


admin.site.register(Entry, LogAdmin)
