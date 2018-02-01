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


admin.site.register(models.Template, TemplateAdmin)
admin.site.register(models.SiteContact, SiteContactAdmin)
