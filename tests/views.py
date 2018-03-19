from django.shortcuts import get_object_or_404, render

from . import models


def article_list(request):
    context = {
        'articles': models.Article.objects.order_by('-id'),
    }
    return render(request, 'tests/index.html', context)


def article_detail(request, article_id, follower_secret=None):
    article = get_object_or_404(models.Article, pk=article_id)
    return render(request, 'tests/detail.html', {'article': article})


def subscribe(request):
    name = request.POST.get('name', '')
    email = request.POST.get('email', '')
    if email == '' or name == '':
        return render(request, 'tests/index.html', {
            'error_message': 'You are missing an email or a name', })

    models.Follower.objects.create(name=name, email=email)
    return render(request, 'tests/subscribed.html')
