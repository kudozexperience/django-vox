from django import forms
from django.contrib import admin

from . import backends, models


class TemplateForm(forms.ModelForm):
    backend = forms.ChoiceField(choices=backends.get_backend_choices())

    class Meta:
        model = models.Template
        fields = ['backend', 'content', 'target', 'is_active']


class TemplateInline(admin.TabularInline):
    model = models.Template
    form = TemplateForm
    min_num = 0
    extra = 0


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'description', 'use_sender',
                    'use_recipient', 'template_count')
    list_filter = ('content_type',)
    inlines = [TemplateInline]

    def get_readonly_fields(self, request, obj=None):
        return ['codename', 'content_type', 'description',
                'use_sender', 'use_recipient']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @staticmethod
    def template_count(obj):
        return obj.template_set.count()


class TemplateAdmin(admin.ModelAdmin):
    list_display = ('notification', 'backend', 'is_active', 'target')
    list_filter = ('notification', 'backend', 'is_active', 'target')


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
admin.site.register(models.Notification, NotificationAdmin)
