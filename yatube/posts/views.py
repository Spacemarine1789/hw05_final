from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm, CommentForm
from .models import Follow, Group, Post, User

PAGE_PER_PAGE = 10


def paging(request, query, obj_per_page):
    paginator = Paginator(query, obj_per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


@cache_page(20, key_prefix='index_page')
def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.select_related('author', 'group')
    page_obj = paging(request, post_list, PAGE_PER_PAGE)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_post(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = paging(request, post_list, PAGE_PER_PAGE)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    post_author = get_object_or_404(User, username=username)
    post_list = post_author.posts.all()
    page_obj = paging(request, post_list, PAGE_PER_PAGE)
    me = request.user
    following = me.is_authenticated and post_author.following.exists()
    context = {
        'post_author': post_author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()
    context = {
        'post': post,
        'form': CommentForm(),
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    if request.method != 'POST':
        form = PostForm()
        context = {
            'form': form,
            'is_edit': False,
        }
        return render(request, 'posts/post_create.html', context)
    form = PostForm(request.POST, files=request.FILES or None)
    if not form.is_valid():
        context = {
            'form': form,
            'is_edit': False,
        }
        return render(request, 'posts/post_create.html', context)
    form.instance.author = request.user
    form.save()
    return redirect('posts:profile', f'{request.user.get_username()}')


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)
    if request.method != 'POST':
        form = PostForm(instance=post)
        context = {
            'form': form,
            'is_edit': True,
        }
        return render(request, 'posts/post_create.html', context)
    form = PostForm(request.POST,
                    instance=post,
                    files=request.FILES or None)
    if not form.is_valid():
        return redirect('posts:post_detail', post_id=post_id)
    form.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    follow = request.user.follower.all()
    follow_list = User.objects.filter(following__in=follow)
    posts = Post.objects.filter(author__in=(follow_list))
    page_obj = paging(request, posts, PAGE_PER_PAGE)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(
            author=author,
            user=request.user
        )
    return redirect('posts:profile', f'{username}')


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    unfollow = get_object_or_404(Follow, user=request.user, author=author)
    unfollow.delete()
    return redirect('posts:profile', f'{username}')
