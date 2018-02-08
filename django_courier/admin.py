from django.contrib import admin
from . import models


class TemplateAdmin(admin.ModelAdmin):
    list_display = ('notification', 'backend', 'is_active')
    list_filter = ('notification', 'backend', 'is_active')


class SiteContactPreferenceInline(admin.TabularInline):
    model = models.SiteContactPreference


class SiteContactAdmin(admin.ModelAdmin):
    inlines = [
        SiteContactPreferenceInline
    ]
    list_display = ('address', 'protocol')


class FailedMessageAdmin(admin.ModelAdmin):
    list_display = ('backend', 'address', 'created_at')
    list_filter = ('backend', 'address')


admin.site.register(models.Template, TemplateAdmin)
admin.site.register(models.SiteContact, SiteContactAdmin)
admin.site.register(models.FailedMessage, FailedMessageAdmin)
