from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator

from django.shortcuts import render, get_object_or_404, redirect

from .models import Post, Group, User

from .forms import PostForm

COUNT = 10


def group_list(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author', 'group')
    paginator = Paginator(posts, COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = 'Записи группы: ' + str(group)
    context = {
        'page_obj': page_obj,
        'group': group,
        'title': title,
        'h1': group.title,
        'description': group.description,
    }
    return render(request, 'posts/group_list.html', context)


def index(request):
    post_list = Post.objects.select_related('author', 'group')
    paginator = Paginator(post_list, COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'posts': post_list,
        'title': 'Последние обновления на сайте',
        'h1': 'Последние обновления на сайте',
    }
    return render(request, 'posts/index.html', context)


def profile(request, username):
    # Здесь код запроса к модели и создание словаря контекста
    user = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=user).select_related(
        'author', 'group')
    paginator = Paginator(post_list, COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': user,
        'h1': 'Все посты пользователя ' + str(user.get_full_name()),
        'title': 'Профайл пользователя ' + str(user.get_full_name()),
        'page_obj': page_obj,
        'h3': page_obj.paginator.count,
        'posts': post_list,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    one_post = get_object_or_404(Post, id=post_id)
    is_author = request.user == one_post.author
    context = {
        'one_post': one_post,
        'title': str(one_post)[:30],
        'is_author': is_author,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    template = 'posts/create_post.html'
    groups = Group.objects.all().order_by('title')
    context = {
        'title': 'Новый пост',
        'form': form,
        'groups': groups,
    }
    if request.method != 'POST':
        return render(request, template, context)
    if not form.is_valid():
        return render(request, template, context)
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', (request.user.username))


@login_required
def post_edit(request, post_id):
    is_edit = True
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None, instance=post)
    groups = Group.objects.all().order_by('title')
    context = {
        'title': 'Редактирование поста',
        'form': form,
        'is_edit': is_edit,
        'post': post,
        'groups': groups,
    }
    if post.author != request.user:
        return redirect('posts:post_detail', (post.pk))
    if request.method != 'POST':
        return render(request, template, context)
    post = form.save()
    return redirect('posts:post_detail', (post.pk))
