import django.template
import django.template.exceptions
import django.conf
from django.core import mail
import json


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
def from_string(text: str, using=None) -> django.template.Template:
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
            return engine.from_string(text)
        except django.template.exceptions.TemplateSyntaxError as e:
            exception = e
    raise exception


# inspired by django-templated-mail
def email_parts(template: django.template.Template, parameters: dict) -> MultipartMessage:
    message = MultipartMessage()
    html_context = django.template.Context(parameters)
    text_context = django.template.Context(parameters, autoescape=False)
    node_parts = {}
    for node in template.template.nodelist:
        name = getattr(node, 'name', None)
        if name is not None:
            node_parts[name] = node

    if 'subject' in node_parts:
        message.subject = node_parts['subject'].render(text_context).strip()
    has_parts = False
    if 'text_body' in node_parts:
        has_parts = True
        message.text = node_parts['text_body'].render(text_context).strip()
    if 'html_body' in node_parts:
        has_parts = True
        message.html = node_parts['html_body'].render(html_context).strip()
    if not has_parts:
        message.text = template.template.render(text_context).strip()
    return message


def email_parts_from_string(text: str, parameters: dict) -> MultipartMessage:
    template = from_string(text)
    return email_parts(template, parameters)

