from django.shortcuts import get_object_or_404, redirect, render

from . import models


def article_list(request):
    context = {
        'articles': models.Article.objects.order_by('-id'),
    }
    return render(request, 'tests/index.html', context)


def article_detail(request, article_id):
    article = get_object_or_404(models.Article, pk=article_id)
    comments = models.Comment.objects.filter(article=article).order_by('id')
    token = request.GET.get('token')
    return render(request, 'tests/detail.html', {
        'article': article, 'comments': comments, 'token': token})


def comment(request, article_id):
    token = request.POST.get('token', '')
    content = request.POST.get('content', '')
    article = get_object_or_404(models.Article, pk=article_id)
    subscriber = models.Subscriber.load_from_token(token)
    models.Comment.objects.create(
        content=content,
        poster=subscriber,
        article=article,
    )
    return redirect('tests:detail', article.id)


def subscribe(request):
    name = request.POST.get('name', '')
    email = request.POST.get('email', '')
    if email == '' or name == '':
        return render(request, 'tests/index.html', {
            'error_message': 'You are missing an email or a name', })

    models.Subscriber.objects.create(name=name, email=email)
    return render(request, 'tests/subscribed.html')
