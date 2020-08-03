from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import EmailPostForm, CommnetForm, SearchForm
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, TrigramSimilarity


def post_list(request, tag_slug=None):
    published_posts = Post.published.all()
    object_list = Post.published.all()

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    # По 3 статьи на каждой странице.
    paginator = Paginator(object_list, 3)
    page = request.GET.get('page')

    try:
        published_posts = paginator.page(page)
    except PageNotAnInteger:
    # Если страница не является целым числом, возвращаем первую страницу.
        published_posts = paginator.page(1)
    except EmptyPage:
    # Если номер страницы больше, чем общее количество страниц, 
    # возвращаем последнюю.
        published_posts = paginator.page(paginator.num_pages)
    return render(request, 'app_blog/post/list.html',
        {'page': page, 
        'published_posts': published_posts,
        'tag': tag})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,
        slug=post,
        status='published',
        date_published__year=year,
        date_published__month=month,
        date_published__day=day)

    comments = post.comments.filter(active=True)
    new_comment = None
    if request.method == 'POST':
        comment_form = CommnetForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommnetForm()

    post_tags_id = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_id).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-date_published')[:4]
    return render(request, 'app_blog/post/detail.html',
        {'post': post,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form,
        'similar_posts': similar_posts, })


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


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Post.objects.annotate(
                search=SearchVector('title', 'body'),
            ).filter(search=query)
            # Триграммный поиск
            # results = Post.objects.annotate(
            #    similarity=TrigramSimilarity('title', query),
            # ).filter(similarity__gt=0.3).order_by('-similarity')
    return render(request, 'app_blog/post/search.html',
        {'form': form,
        'query': query,
        'results': results})
