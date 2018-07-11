from typing import List

import django.conf
import django.core.mail.backends.base
import django.core.mail.backends.smtp
import django.template
import django.utils.html
from django.template import Context

import django_vox.base

__ALL__ = ('Backend', 'template_from_string')


def html_format(text: str):
    escaped = django.utils.html.escape(text)
    return escaped.replace('\r\n', '<br/>').replace('\n', '<br/>')


class AttachmentData:
    def __init__(self, data: bytes, mime: str):
        self.data = data
        self.mime = mime


class Backend:

    USE_SUBJECT = False
    USE_ATTACHMENTS = False
    ESCAPE_HTML = True
    DEPENDS = ()

    @classmethod
    def build_message(cls, subject: str, body: str, parameters: dict,
                      attachments: List[AttachmentData]):
        template = template_from_string(body)
        context = Context(parameters, autoescape=cls.ESCAPE_HTML)
        return template.render(context)

    @classmethod
    def preview_message(cls, subject: str, body: str, parameters: dict):
        message = cls.build_message(subject, body, parameters, [])
        if not cls.ESCAPE_HTML:
            message = html_format(message)
        return message

    @classmethod
    def add_attachment(cls, data: bytes, mime: str):
        pass  # not supported

    @classmethod
    def send_message(cls, contact: django_vox.base.Contact, message: str):
        raise NotImplementedError


def template_from_string(text: str, using=None) -> \
        django.template.base.Template:
    """
    Convert a string into a template object,
    using a given template engine or using the default backends
    from settings.TEMPLATES if no engine was specified.
    """
    # This function is based on django.template.loader.get_template,
    # but uses Engine.from_string instead of Engine.get_template.
    engines = django.template.engines
    engine_list = engines.all() if using is None else [engines[using]]
    exception = None
    for engine in engine_list:
        try:
            return engine.from_string(text).template
        except django.template.exceptions.TemplateSyntaxError as e:
            exception = e
    raise exception
