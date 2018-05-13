import django.contrib.messages
import django.forms.utils
import django.http
from django import forms
from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.admin.utils import unquote
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.core.exceptions import PermissionDenied, ValidationError
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.html import escape
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

from . import models, registry


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


class TemplateInlineFormSet(forms.BaseInlineFormSet):
    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs['notification'] = self.instance
        return kwargs


class TemplateForm(forms.ModelForm):
    backend = BackendChoiceField(choices=registry.backends.all())
    recipient = forms.ChoiceField()

    class Meta:
        model = models.Template
        fields = ['notification', 'backend', 'subject', 'content',
                  'recipient', 'enabled']

    def __init__(self, notification=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['recipient'].choices = \
            self.get_recipient_choices(notification)

    def clean(self):
        data = self.cleaned_data
        notification = data['notification']
        try:
            notification.preview(data['backend'], data['content'])
        except Exception as exc:
            raise ValidationError(str(exc))

    @staticmethod
    def get_recipient_choices(notification):
        recipient_models = notification.get_recipient_models()
        for recipient_key, model in recipient_models.items():
            channel_data = registry.channels[model].prefix(recipient_key)
            for key, channel in channel_data.items():
                yield key, channel.name


class SiteContactForm(forms.ModelForm):
    protocol = forms.ChoiceField(choices=registry.get_protocol_choices())

    class Meta:
        model = models.SiteContact
        fields = ['name', 'protocol', 'address', 'enable_filter']


class NotificationForm(forms.ModelForm):

    class Meta:
        model = models.Notification
        fields = ['codename', 'content_type', 'description', 'target_model']


class NotificationIssueForm(forms.Form):

    contents = forms.ModelMultipleChoiceField(
        queryset=None, label=_('Objects'),
        widget=FilteredSelectMultiple(
            verbose_name=_('Objects'), is_stacked=False),
        help_text=_('A separate notification will be issued for each object.')
    )

    def __init__(self, notification, *args, **kwargs):
        self.notification = notification
        model_cls = notification.content_type.model_class()
        self.declared_fields['contents'].queryset = model_cls.objects
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        if not commit:
            return
        contents = self.cleaned_data['contents']
        for content in contents:
            self.notification.issue(content)


class TemplateInline(admin.StackedInline):
    model = models.Template
    form = TemplateForm
    formset = TemplateInlineFormSet
    min_num = 0
    extra = 0


class NotificationAdmin(admin.ModelAdmin):
    change_form_template = 'django_vox/notification/change_form.html'
    list_display = ('__str__', 'description', 'required', 'template_count')
    list_filter = ('content_type',)
    inlines = [TemplateInline]
    form = NotificationForm
    issue_form = NotificationIssueForm
    issue_template = 'django_vox/notification/issue.html'

    fields = ['codename', 'content_type', 'description']

    class Media:
        css = {
            'all': ('django_vox/markitup/images.css',
                    'django_vox/markitup/style.css'),
        }
        js = ('django_vox/markitup/jquery.markitup.js',
              'django_vox/notification_fields.js')

    # only show inlines on change forms
    def get_inline_instances(self, request, obj=None):
        return obj and super().get_inline_instances(request, obj) or []

    def get_urls(self):
        return [
            url(
                r'^(?P<id>\w+)/preview/(?P<backend_id>.+)/$',
                self.admin_site.admin_view(self.preview),
                name='django_vox_preview'),
            url(
                r'^(?P<id>\w+)/variables/$',
                self.admin_site.admin_view(self.variables),
                name='django_vox_variables'),
            url(
                r'^(?P<id>\w+)/issue/$',
                self.admin_site.admin_view(self.issue),
                name='django_vox_issue'),
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
        result = notification.get_recipient_variables()
        return django.http.JsonResponse(result, safe=False)

    def issue(self, request, id, form_url=''):
        if not self.has_change_permission(request):
            raise PermissionDenied
        notification = self.get_object(request, unquote(id))
        if notification is None:
            raise django.http.Http404(
                _('%(name)s object with primary key %(key)r does not exist.')
                % {'name': force_text(self.model._meta.verbose_name),
                   'key': escape(id)})
        if request.method == 'POST':
            form = self.issue_form(notification, request.POST)
            if form.is_valid():
                form.save()
                msg = ugettext('Notification sent successfully.')
                django.contrib.messages.success(
                    request, msg, fail_silently=True)
                return django.http.HttpResponseRedirect(
                    reverse(
                        '%s:%s_%s_change' % (
                            self.admin_site.name,
                            notification._meta.app_label,
                            notification._meta.model_name,
                        ),
                        args=(notification.pk,),
                    )
                )
        elif request.method == 'GET':
            form = self.issue_form(notification)
        else:
            return django.http.HttpResponseNotAllowed(('POST',))

        fieldsets = [(None, {'fields': list(form.base_fields)})]
        admin_form = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            'title': _('Send notification: %s') % escape(str(notification)),
            'media': self.media + admin_form.media,
            'form_url': form_url,
            'form': form,
            'is_popup': (IS_POPUP_VAR in request.POST or
                         IS_POPUP_VAR in request.GET),
            'add': True,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': self.model._meta,
            'original': notification,
            'save_as': False,
            'show_save': True,
        }
        context.update(self.admin_site.each_context(request))
        request.current_app = self.admin_site.name

        return TemplateResponse(request, self.issue_template, context)

    def get_readonly_fields(self, request, obj=None):
        if self.has_delete_permission(request, obj):
            return ['content_type'] if obj else []
        return ['codename', 'content_type', 'description', 'required',
                'source_model', 'target_model']

    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return super().has_delete_permission(request)
        return super().has_delete_permission(request) and not obj.from_code

    def save_form(self, request, form, change):
        result = super().save_form(request, form, change)
        if not change:
            result.from_code = False
        return result

    @staticmethod
    def template_count(obj):
        return obj.template_set.count()


class SiteContactSettingInline(admin.TabularInline):
    model = models.SiteContactSetting


class SiteContactAdmin(admin.ModelAdmin):
    form = SiteContactForm
    inlines = [SiteContactSettingInline]
    list_display = ('name', 'address', 'protocol')


class FailedMessageAdmin(admin.ModelAdmin):
    list_display = ('backend', 'address', 'created_at')
    list_filter = ('backend', 'address')


admin.site.register(models.SiteContact, SiteContactAdmin)
admin.site.register(models.FailedMessage, FailedMessageAdmin)
admin.site.register(models.Notification, NotificationAdmin)