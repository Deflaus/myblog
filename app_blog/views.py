from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


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
