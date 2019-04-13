from django.contrib import admin
import django_vox.admin

from . import models


class UserAdmin(admin.ModelAdmin):
    actions = (django_vox.admin.notify,)


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Article)
admin.site.register(models.Subscriber)
admin.site.register(models.Comment)
