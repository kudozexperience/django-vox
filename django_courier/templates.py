import json
import random
import re

import django.conf
import django.template
import django.template.exceptions
from django.core import mail
from django.db.models import NOT_PROVIDED

from . import settings, base


class MultipartMessage:

    def __init__(self):
        self.subject = ''
        self.text = ''
        self.html = ''

    @classmethod
    def from_dict(cls, obj):
        result = cls()
        result.subject = obj.get('subject')
        result.text = obj.get('text')
        result.html = obj.get('html')
        return result

    @classmethod
    def from_string(cls, string):
        return cls.from_dict(json.loads(string))

    def to_dict(self):
        return {'subject': self.subject, 'text': self.text, 'html': self.html}

    def __str__(self):
        return json.dumps(self.to_dict())

    def to_mail(self) -> mail.EmailMultiAlternatives:
        email = mail.EmailMultiAlternatives()
        email.subject = self.subject
        if self.text:
            email.body = self.text
            if self.html:
                email.attach_alternative(self.html, 'text/html')
        elif self.html:
            email.body = self.html
            email.content_subtype = 'html'
        return email


# from https://stackoverflow.com/questions/2167269/
def from_string(text: str, using=None) -> django.template.base.Template:
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


# inspired by django-templated-mail
def email_parts(subject: str, body: str, parameters: dict) -> MultipartMessage:
    message = MultipartMessage()
    html_context = django.template.Context(parameters)
    text_context = django.template.Context(parameters, autoescape=False)
    node_parts = {}
    subject_template = from_string(subject)
    body_template = from_string(body)
    message.subject = subject_template.render(text_context)

    for node in body_template.nodelist:
        name = getattr(node, 'name', None)
        if name is not None:
            node_parts[name] = node

    with html_context.bind_template(body_template):
        with text_context.bind_template(body_template):
            if 'subject' in node_parts:
                message.subject = node_parts['subject'].render(
                    text_context).strip()
            has_parts = False
            if 'text_body' in node_parts:
                has_parts = True
                message.text = node_parts['text_body'].render(
                    text_context).strip()
            if 'html_body' in node_parts:
                has_parts = True
                message.html = node_parts['html_body'].render(
                    html_context).strip()
            if not has_parts:
                message.text = body_template.render(text_context).strip()
    return message


class MarkdownParameters:

    MD_SPECIAL_PATTERN = re.compile(r"[\\\`\*\_\{\}\[\]\(\)\#\+\-\.\!]")

    def __init__(self, obj):
        self._obj = obj

    def __contains__(self, item):
        return self._obj.__contains__(item)

    def __getitem__(self, item):
        obj = self._obj[item]
        if callable(obj):
            return CallableMarkdownParameters(obj)
        return MarkdownParameters(obj)

    def __getattr__(self, attr):
        obj = getattr(self._obj, attr)
        if callable(obj):
            return CallableMarkdownParameters(obj)
        return MarkdownParameters(obj)

    def __str__(self):
        return self.MD_SPECIAL_PATTERN.sub(self.escape, str(self._obj))

    @staticmethod
    def escape(patterns) -> str:
        return '\\' + patterns[0]


class CallableMarkdownParameters(MarkdownParameters):

    def __call__(self, *args, **kwargs):
        obj = self._obj.__call__(*args, **kwargs)
        if callable(obj):
            return CallableMarkdownParameters(obj)
        return MarkdownParameters(obj)


def email_md(subject: str, body: str, parameters: dict) -> MultipartMessage:
    import markdown2
    md_parameters = MarkdownParameters(parameters)
    text_context = django.template.Context(parameters, autoescape=False)
    md_context = django.template.Context(md_parameters, autoescape=False)
    message = MultipartMessage()
    subject_template = from_string(subject)
    body_template = from_string(body)
    message.subject = subject_template.render(text_context)
    message.text = body_template.render(text_context)
    md_body = body_template.render(md_context)
    message.html = markdown2.markdown(
        md_body, extras=settings.MARKDOWN_EXTRAS,
        link_patterns=settings.MARKDOWN_LINK_PATTERNS)
    return message


def make_model_preview(content_type):
    obj = content_type.objects.first()
    if obj is not None:
        return obj
    obj = content_type()
    for field in content_type._meta.fields:
        value = None
        if field.default != NOT_PROVIDED:
            value = field.default
        if not value:
            desc = str(field.description).lower()
            if desc.startswith('string'):
                value = '{{{}}}'.format(field.verbose_name)
            elif desc.startswith('integer'):
                value = random.randint(1, 100)
            else:
                pass
        setattr(obj, field.attname, value)
    return obj


class PreviewParameters:

    def __init__(self, content_type, sender_model, recipient_model):
        self.recipient = (make_model_preview(recipient_model)
                          if recipient_model else {})
        self.sender = (make_model_preview(sender_model)
                       if sender_model else {})
        self.contact = base.Contact(
            'Contact Name', 'email', 'contact@example.org')
        self.content = make_model_preview(content_type)

    def __contains__(self, item):
        return item in ('contact', 'recipient', 'sender', 'content')

    def __getitem__(self, attr):
        obj = getattr(self, attr)
        return ProxyParameters(obj)


class ProxyParameters:

    def __init__(self, obj):
        self._obj = obj

    def __contains__(self, item):
        return self._obj.__contains__(item)

    def __getitem__(self, item):
        obj = self._obj[item]
        if callable(obj):
            return CallableProxyParameters(obj)
        return ProxyParameters(obj)

    def __getattr__(self, attr):
        obj = getattr(self._obj, attr)
        if callable(obj):
            return CallableProxyParameters(obj)
        return ProxyParameters(obj)

    def __str__(self):
        return str(self._obj)


class CallableProxyParameters(ProxyParameters):
    def __call__(self, *args, **kwargs):
        obj = self._obj.__call__(*args, **kwargs)
        if callable(obj):
            return CallableProxyParameters(obj)
        return ProxyParameters(obj)
