from http import HTTPStatus
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая запись 1',
        )
        cls.templates_pages_names_public = {
            '/': 'posts/index.html',
            '/group/test_group/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            f'/posts/{cls.post.pk}/': ('posts/post_detail.html'),
        }
        cls.templates_pages_names_private = {
            '/': 'posts/index.html',
            '/group/test_group/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            f'/posts/{cls.post.pk}/': ('posts/post_detail.html'),
            '/create/': 'posts/post_create.html',
        }

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_urls_guest_uses_correct_location(self):
        """URL-адрес доступен гостю."""

        for address, template in self.templates_pages_names_public.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_authorized_uses_correct_location(self):
        """URL-адрес доступен авторизованому пользователю"""

        for address, template in self.templates_pages_names_private.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_author_uses_correct_location(self):
        """URL-адрес доступен автору"""
        test_post = Post.objects.create(
            author=self.user,
            text='Тестовый пост зарегестрированого пользователя'
        )
        address = f'/posts/{test_post.pk}/edit/'
        template = 'posts/post_create.html'
        response = self.authorized_client.get(address)
        self.assertTemplateUsed(response, template)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_doesnt_exist(self):
        """Проверка несуществующей страницы"""
        address = '/doesnt_exist/'
        response = self.authorized_client.get(address)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
