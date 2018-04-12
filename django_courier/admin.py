import django.http
from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin.utils import unquote
from django.core.exceptions import PermissionDenied
from django.utils.encoding import force_text
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _

from . import backends, models
from django import forms

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


class SelectWithSubjectData(forms.Select):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_subjects = {}

    def create_option(self, name, value, label, selected,
                      index, subindex=None, attrs=None):
        index = str(index) if subindex is None else "%s_%s" % (index, subindex)
        option_attrs = {'data-subject': ('true' if self.use_subjects.get(value)
                                         else 'false')}
        if selected:
            option_attrs.update(self.checked_attribute)
        if 'id' in option_attrs:
            option_attrs['id'] = self.id_for_label(option_attrs['id'], index)
        return {
            'name': name,
            'value': value,
            'label': label,
            'selected': selected,
            'index': index,
            'attrs': option_attrs,
            'type': self.input_type,
            'template_name': self.option_template_name,
        }


class BackendChoiceField(forms.ChoiceField):
    widget = SelectWithSubjectData

    def __init__(self, choices=(), *args, **kwargs):
        backs = list(choices)
        choice_pairs = [(back.ID, back.VERBOSE_NAME) for back in backs]
        use_subjects = dict([(back.ID, back.USE_SUBJECT) for back in backs])
        super().__init__(choices=choice_pairs, *args, **kwargs)
        self.widget.use_subjects = use_subjects


class TemplateForm(forms.ModelForm):
    backend = BackendChoiceField(choices=backends.get_backends())
    target = forms.ChoiceField(choices=models.get_target_choices())

    class Meta:
        model = models.Template
        fields = ['notification', 'backend', 'subject', 'content',
                  'target', 'is_active']


class SiteContactForm(forms.ModelForm):
    protocol = forms.ChoiceField(choices=backends.get_protocol_choices())

    class Meta:
        model = models.SiteContact
        fields = ['name', 'protocol', 'address']


class TemplateInline(admin.StackedInline):
    model = models.Template
    form = TemplateForm
    min_num = 0
    extra = 0


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'description', 'use_sender',
                    'use_recipient', 'required', 'template_count')
    list_filter = ('content_type',)
    inlines = [TemplateInline]

    fields = ['codename', 'content_type', 'description',
              'use_sender', 'use_recipient']

    class Media:
        css = {
            'all': ('django_courier/markitup/images.css',
                    'django_courier/markitup/style.css'),
        }
        js = ('django_courier/markitup/jquery.markitup.js',
              'django_courier/notification_fields.js')

    def get_urls(self):
        return [
                   url(
                       r'^(?P<id>\w+)/preview/(?P<backend_id>.+)/$',
                       self.admin_site.admin_view(self.preview),
                       name='django_courier_preview'),
                   url(
                       r'^(?P<id>\w+)/variables/$',
                       self.admin_site.admin_view(self.variables),
                       name='django_courier_variables'),
            ] + super().get_urls()

    def preview(self, request, id, backend_id):
        if not self.has_change_permission(request):
            raise PermissionDenied
        notification = self.get_object(request, unquote(id))
        if notification is None:
            raise django.http.Http404(
                _('%(name)s object with primary key %(key)r does not exist.')
                % {'name': force_text(self.model._meta.verbose_name),
                   'key': escape(id)})
        if request.method != 'POST':
            return django.http.HttpResponseNotAllowed(('POST',))
        try:
            result = notification.preview(backend_id, request.POST['body'])
        except Exception as exc:
            result = 'Unable to make preview: {}'.format(str(exc))
        return django.http.HttpResponse(result)

    def variables(self, request, id):
        if not self.has_change_permission(request):
            raise PermissionDenied
        notification = self.get_object(request, unquote(id))
        if notification is None:
            raise django.http.Http404(
                _('%(name)s object with primary key %(key)r does not exist.')
                % {'name': force_text(self.model._meta.verbose_name),
                   'key': escape(id)})
        if request.method != 'POST':
            return django.http.HttpResponseNotAllowed(('POST',))
        result = notification.get_variables()
        return django.http.JsonResponse(result, safe=False)

    def get_readonly_fields(self, request, obj=None):
        return ['codename', 'content_type', 'description',
                'use_sender', 'use_recipient', 'required',
                'sender_model', 'recipient_model']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @staticmethod
    def template_count(obj):
        return obj.template_set.count()


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


admin.site.register(models.SiteContact, SiteContactAdmin)
admin.site.register(models.FailedMessage, FailedMessageAdmin)
admin.site.register(models.Notification, NotificationAdmin)
