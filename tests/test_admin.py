from django.test import TestCase

from . import models


class VariableTests(TestCase):
    """Test the variables that are used in admin"""

    fixtures = ['test']

    @staticmethod
    def test_variables():
        notification = models.Article.get_notification('created')
        variables = notification.get_recipient_variables()
        assert variables.keys() == {'si', 'c:sub', 'c:author', '_static'}
        # check recipient variables first:
        for key in ('si', 'c:sub', 'c:author'):
            assert variables[key]['value'] == 'recipient'
        static = variables['_static']
        assert len(static) == 1
        assert static[0]['label'] == 'Article'
        assert static[0]['value'] == 'content'
