from django.contrib import admin

from . import models

admin.site.register(models.User)
admin.site.register(models.Article)
admin.site.register(models.Follower)
admin.site.register(models.Comment)
