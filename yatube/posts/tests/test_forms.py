import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from posts.models import Comment, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Новый тестовый пост зарегестрированого пользователя',
            id=1
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.get(username='auth')
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст записи для формы',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.auth_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user.username}),
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        new_post = Post.objects.get(id=2)
        self.assertEqual(new_post.author, self.user)
        self.assertEqual(new_post.text, 'Тестовый текст записи для формы')
        self.assertEqual(new_post.group, self.group)
        self.assertEqual(new_post.image, 'posts/small.gif')

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post."""
        post_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small1.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст записи для формы',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.auth_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': (f'{self.post.pk}')}
                    ),
            data=form_data,
            follow=True
        )

        self.assertRedirects(
            response,
            reverse('posts:post_detail',
                    kwargs={'post_id': (f'{self.post.pk}')}),
        )
        self.assertEqual(Post.objects.count(), post_count)
        new_post = Post.objects.get(id=1)
        self.assertEqual(new_post.author, self.user)
        self.assertEqual(new_post.text, 'Тестовый текст записи для формы')
        self.assertEqual(new_post.group, self.group)
        self.assertEqual(new_post.image, 'posts/small1.gif')

    def test_create_comment(self):
        """Валидная форма создает коментарий Comment."""
        comment_count = Comment.objects.count()
        form_data = {
            'post': self.post,
            'author': self.user,
            'text': "Мне нравится эта запись",
        }
        response = self.auth_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': (f'{self.post.pk}')}
                    ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail',
                    kwargs={'post_id': (f'{self.post.pk}')}),
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        new_comment = Comment.objects.get(id=1)
        self.assertEqual(new_comment.author, self.user)
        self.assertEqual(new_comment.text, 'Мне нравится эта запись')
        self.assertEqual(new_comment.post, self.post)

    def test_no_create_comment(self):
        """Валидная форма не создает коментарий, если автор не автоизован."""
        comment_count = Comment.objects.count()
        form_data = {
            'post': self.post,
            'author': self.user,
            'text': "Мне нравится эта запись",
        }
        # тестируру отправку формы не авторизованым клиентом
        response = self.client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': (f'{self.post.pk}')}
                    ),
            data=form_data,
            follow=True
        )
        # проверяю что новый комент не добавился
        self.assertEqual(Comment.objects.count(), comment_count)
        self.assertEqual(response.status_code, 200)
