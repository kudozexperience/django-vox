from unittest import mock

import django.http
from django.contrib.admin import AdminSite
from django.test import TestCase

import django_vox.admin
import django_vox.models

from . import models


class MockSuperUser:

    is_active = True
    is_staff = True

    @staticmethod
    def has_perm(_perm):
        return True


class MockRequest:

    def __init__(self, method, parameters=None):
        self.method = method
        self.user = MockSuperUser()
        self.GET = {}
        self.POST = {}
        if parameters is not None:
            if method == 'POST':
                self.POST = parameters
            else:
                self.GET = parameters
        self.META = {'SCRIPT_NAME': ''}


class VariableTests(TestCase):
    """Test the variables that are used in admin"""

    fixtures = ['test']

    @staticmethod
    def test_variables():
        notification = models.Article.get_notification('created')
        variables = notification.get_recipient_variables()
        assert {'si', 'c:sub', 'c:author', '_static'} == variables.keys()
        # check recipient variables first:
        for key in ('si', 'c:sub', 'c:author'):
            assert variables[key]['value'] == 'recipient'
        static = variables['_static']
        assert len(static) == 1
        assert static[0]['label'] == 'Article'
        assert static[0]['value'] == 'content'


class NotificationAdminTests(TestCase):
    """Test NotificationAdmin"""

    fixtures = ['test']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_class = django_vox.models.Notification
        self.admin = django_vox.admin.NotificationAdmin(
            self.model_class, AdminSite())

    def test_template_count(self):
        model_obj = self.model_class.objects.get_by_natural_key(
            'tests', 'article', 'created')
        assert 2 == self.admin.template_count(model_obj)

    def test_get_urls(self):
        names = (u.name for u in self.admin.get_urls() if u.name is not None)
        name_set = set((un for un in names
                        if not un.startswith('django_vox_notification')))
        assert 3 == len(name_set)
        expected = {'django_vox_issue', 'django_vox_preview',
                    'django_vox_variables'}
        assert expected == name_set

    def test_fields(self):
        base_fields = ['codename', 'content_type', 'description']
        from_code_ro = ['codename', 'content_type', 'description',
                        'required', 'source_model', 'target_model']
        new_obj = self.model_class()
        model_obj = self.model_class.objects.get_by_natural_key(
            'tests', 'article', 'created')
        request = MockRequest('GET')
        assert base_fields == self.admin.get_fields(request)
        assert [] == self.admin.get_readonly_fields(request)
        assert ['content_type'] == self.admin.get_readonly_fields(
            request, new_obj)
        assert from_code_ro == self.admin.get_readonly_fields(
            request, model_obj)

    def test_issue(self):
        notification = self.model_class.objects.get_by_natural_key(
            'tests', 'article', 'created')
        obj = models.Article.objects.first()
        with mock.patch('django_vox.models.Notification.issue'):
            # no POST parameters, so won't be valid
            request = MockRequest('POST', {})
            response = self.admin.issue(request, str(notification.id))
            assert response.status_code == 200
            assert 'This field is required' in response.rendered_content
            # this should 404
            with self.assertRaises(django.http.Http404):
                self.admin.issue(request, '9000')
            # this POST should work
            # we have to perform some malarky because of an isinstance
            # check in django 1.10
            request = MockRequest('POST', {'contents': (obj.id,)})
            mock_request = mock.Mock(spec=django.http.HttpRequest)
            for attr in request.__dir__():
                if not attr.startswith('_'):
                    setattr(mock_request, attr, getattr(request, attr))
            response = self.admin.issue(mock_request, str(notification.id))
            assert response.status_code == 302
