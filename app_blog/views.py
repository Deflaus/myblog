from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import EmailPostForm


def post_list(request):
    published_posts = Post.published.all()
    object_list = Post.published.all()
    # По 3 статьи на каждой странице.
    paginator = Paginator(object_list, 3)
    page = request.GET.get('page')

    try:
        published_posts = paginator.page(page)
    except PageNotAnInteger:
    # Если страница не является целым числом, возвращаем первую страницу.
        published_posts = paginator.page(1)
    except EmptyPage:
    # Если номер страницы больше, чем общее количество страниц, возвращаем последнюю.
        published_posts = paginator.page(paginator.num_pages)
    return render(request,
        'app_blog/post/list.html',
        {'page': page, 'published_posts': published_posts})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,
        slug=post,
        status='published',
        date_published__year=year,
        date_published__month=month,
        date_published__day=day)
    return render(request, 'app_blog/post/detail.html', {'post': post})


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) рекомендует к прочтению "{}"'.format(cd['name'],
                                                                   cd['email'],
                                                                   post.title)
            message = 'Прочитайте "{}" по ссылке {}\n\nКомментарий ' \
            'пользователя {}: {}'.format(post.title, post_url, cd['name'],
                                        cd['comments'])
            send_mail(subject, message, 'snow41521@gmail.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'app_blog/post/share.html',
        {'post': post,
        'form': form,
        'sent': sent})
