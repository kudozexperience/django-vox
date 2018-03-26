from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from . import backends, models

# Generic things


class TargetFilter(admin.SimpleListFilter):
    """A really simple filter so that we have the right labels
    """
    title = _('target')
    parameter_name = 'target'

    def lookups(self, request, model_admin):
        """Return list of key/name tuples
        """
        return models.get_target_choices()

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(target=self.value())
        return queryset


def target_field(obj):
    return models.get_targets().get(obj.target, obj.target)


class TemplateForm(forms.ModelForm):
    backend = forms.ChoiceField(choices=backends.get_backend_choices())
    target = forms.ChoiceField(choices=models.get_target_choices())

    class Meta:
        model = models.Template
        fields = ['notification', 'backend', 'content', 'target', 'is_active']


class SiteContactForm(forms.ModelForm):
    protocol = forms.ChoiceField(choices=backends.get_protocol_choices())

    class Meta:
        model = models.SiteContact
        fields = ['name', 'protocol', 'address']


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
    list_display = ('notification', 'backend', 'is_active', target_field)
    list_filter = ('notification', 'backend', 'is_active', TargetFilter)
    form = TemplateForm


class SiteContactPreferenceInline(admin.TabularInline):
    model = models.SiteContactPreference


class SiteContactAdmin(admin.ModelAdmin):
    form = SiteContactForm
    inlines = [
        SiteContactPreferenceInline
    ]
    list_display = ('name', 'address', 'protocol')


class FailedMessageAdmin(admin.ModelAdmin):
    list_display = ('backend', 'address', 'created_at')
    list_filter = ('backend', 'address')


admin.site.register(models.Template, TemplateAdmin)
admin.site.register(models.SiteContact, SiteContactAdmin)
admin.site.register(models.FailedMessage, FailedMessageAdmin)
admin.site.register(models.Notification, NotificationAdmin)
