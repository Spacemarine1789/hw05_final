from django import forms
from .models import Comment, Post


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст записи',
            'group': 'Группа',
            'image': 'Картинка',
        }
        help_texts = {
            'text': ('Введите текст записи'),
            'group': ('Выберете группу'),
            'image': ('Загрузите картинку'),
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Текст комментария',
        }
        help_texts = {
            'text': ('Введите текст комментария'),
        }
