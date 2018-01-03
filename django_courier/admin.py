from django.contrib import admin
from . import models


class TemplateAdmin(admin.ModelAdmin):
    list_display = ('notification', 'backend', 'is_active')
    list_filter = ('notification', 'backend', 'is_active')


admin.site.register(models.Template, TemplateAdmin)
