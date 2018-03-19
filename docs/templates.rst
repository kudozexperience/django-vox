Notification Templates
======================

Email Templates
---------------

Email templates are a bit more complicated because they have to specify a
header, and optionally a text/html section. To achieve this, we use
the ``block`` feature in django templates. An example email might look
something like::

    {% block subject %}Comment notification{% endblock %}
    {% block text_body %}Hi {{ recipient.name }},

    {{ sender.name }} has posted a comment on your blog titled
    {{ content.article.title }}.{% endblock %}
    {% block html_body %}<p>Hi {{ recipient.name }},</p>

    <p>{{ sender.name }} has posted a comment on your blog titled
    {{ content.article.title }}.</p>{% endblock %}
