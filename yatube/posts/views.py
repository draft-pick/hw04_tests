from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from .models import Post, Group, User
from .forms import PostForm
from .utils import paginator_posts


def index(request):
    """Главная страница."""

    template = 'posts/index.html'
    title = 'Последние обновления на сайте'
    posts = Post.objects.all()
    page_obj = paginator_posts(request, posts)

    context = {
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    """Посты, отфильтрованные по группам."""

    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.group_posts.all()
    page_obj = paginator_posts(request, posts)

    context = {
        'title': f'Записи сообщества {group.title}',
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    """Публикация нового поста."""

    form = PostForm(request.POST or None)
    template = 'posts/create_post.html'

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author)

    context = {
        'title': 'Публикация нового поста',
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    """Редактирование поста."""

    post = get_object_or_404(Post, pk=post_id)
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None, instance=post)

    if request.method == 'GET':
        if request.user.pk != post.author.pk:
            return redirect('posts:post_detail', post_id=post.id)
        context = {
            'title': 'Редактировать запись',
            'form': form,
            'is_edit': True,
            'post': post,
        }
        return render(request, template, context)

    if request.method == 'POST':
        if form.is_valid() and request.user.pk == post.author.pk:
            form.save()
            return redirect('posts:post_detail', post_id=post.id)

        elif request.user.pk != post.author.pk:
            return redirect('posts:post_detail', post_id=post.id)


def post_detail(request, post_id):
    """Просмотр поста."""

    view_post = get_object_or_404(Post, pk=post_id)

    context = {
        'title': view_post.text[:30],
        'view_post': view_post,
    }
    return render(request, 'posts/post_detail.html', context)


def profile(request, username):
    """Профайл пользователя."""

    author_name = get_object_or_404(User, username=username)
    posts_list = author_name.posts.all()
    page_obj = paginator_posts(request, posts_list)

    context = {
        'title': f"""Профайл пользователя
                     {author_name.first_name}
                     {author_name.last_name}
            """,
        'author_name': author_name,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)
