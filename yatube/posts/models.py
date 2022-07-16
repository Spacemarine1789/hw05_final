from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название группы',
        help_text='Введите название группы',
    )
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(
        verbose_name='Описание группы',
        help_text='Введите название группы',
    )

    def __str__(self) -> str:
        return str(self.title)


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст записи',
        help_text='Введите текст записи'
    )
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Название группы',
        help_text='Выберете название группы',
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        verbose_name='Картинка',
        help_text='Загрузите картинку',
    )

    def __str__(self) -> str:
        return str(self.text[:15])

    class Meta:
        ordering = ['-pub_date']


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите текст комментария',
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )
