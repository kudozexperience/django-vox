import django.template
import django.template.exceptions
import django.conf
from django.core import mail


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
def email_parts(
        template: django.template.Template,
        parameters: dict) -> mail.EmailMultiAlternatives:
    email = mail.EmailMultiAlternatives()
    context = django.template.Context(parameters)
    parts = {}
    for node in template.template.nodelist:
        name = getattr(node, 'name', None)
        if name is not None:
            parts[name] = node.render(context).strip()

    email.subject = parts.get('subject', '')
    if 'text_body' in parts:
        email.body = parts['text_body']
        if 'html_body' in parts:
            email.attach_alternative(parts['html_body'], 'text/html')
    elif 'html_body' in parts:
        email.body = parts['html_body']
        email.content_subtype = 'html'
    else:
        email.body = template.template.render(context).strip()
    return email


def parts_from_string(text: str, parameters: dict) -> mail.EmailMultiAlternatives:
    template = from_string(text)
    return email_parts(template, parameters)

