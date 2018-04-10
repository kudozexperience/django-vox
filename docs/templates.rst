Notification Templates
======================

Notification templates use django's build-in, templating system. This
gives us more than enough power to craft the kind of message we want,
without making things too onerous.

Subjects
--------

Templates have a subject field which is sometimes used, depending on
the backend. Any backend which supports a subject, has the attribute
``USE_SUBJECT`` set to ``True``. Setting a subject on a template
who's backend doesn't use it has no effect.


Template-base Email Backend
---------------------------

The template-based email backend a fair bit more complicated because
they use the template content to specify the subject, and a text
and/or html component to the email. This is done by using
the ``block`` feature in django templates. An example email might look
something like::

    {% block subject %}Comment notification{% endblock %}
    {% block text_body %}Hi {{ recipient.name }},

    {{ sender.name }} has posted a comment on your blog titled
    {{ content.article.title }}.{% endblock %}
    {% block html_body %}<p>Hi {{ recipient.name }},</p>

    <p>{{ sender.name }} has posted a comment on your blog titled
    {{ content.article.title }}.</p>{% endblock %}

If this seems a little complicated, the markdown-based email backend
might be preferable.
