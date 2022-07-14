import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from posts.models import Follow, Group, Post
from posts.forms import PostForm

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая запись 1',
            group=cls.group,
            image=uploaded
        )
        cls.templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test-group'}): (
                'posts/group_list.html'),
            reverse('posts:profile', kwargs={'username': 'auth'}): (
                'posts/profile.html'),
            reverse('posts:post_detail',
                    kwargs={'post_id': (f'{cls.post.pk}')}
                    ): ('posts/post_detail.html'),
            reverse('posts:post_create'): 'posts/post_create.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': (f'{cls.post.pk}')}
                    ): ('posts/post_create.html'),
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.get(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        contex_page = {
            self.post.author: first_object.author,
            self.post.text: first_object.text,
            self.post.image: first_object.image,
            self.post.group.title: first_object.group.title,
            self.post.group.slug: first_object.group.slug,
            self.post.group.description: first_object.group.description
        }
        for expected, value in contex_page.items():
            with self.subTest():
                self.assertEqual(value, expected)

    def test_cache(self):
        """Тестирование кэша"""
        test_post = Post.objects.create(
            author=self.user,
            text='Новый пост для проверки кэша'
        )
        # получаю контент страницы до удаления поста
        response_1 = self.authorized_client.get(reverse('posts:index'))
        posts_1 = response_1.content
        test_post.delete()
        # получаю кэшированй контент страницы после удаления поста поста
        response_2 = self.authorized_client.get(reverse('posts:index'))
        posts_2 = response_2.content
        self.assertEqual(posts_2, posts_1)
        cache.clear()
        # получаю не кэшированй контент страницы после удаления поста поста
        response_3 = self.authorized_client.get(reverse('posts:index'))
        posts_3 = response_3.content
        self.assertNotEqual(posts_3, posts_1)
        self.assertNotEqual(posts_3, posts_2)

    def test_group_list_page_show_correct_post(self):
        # Здесь я проверяю что пост с другой группой не будет выведен
        # на страницу со старой группой.
        group1 = Group.objects.create(
            title='Тестовая группа 1',
            slug='test-group-1',
            description='Тестовое описание 1',
        )
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-group'})
        )
        group_object = response.context['group']
        post_objects = response.context['page_obj']
        # проверяю контекст группы
        self.assertEqual(group_object, self.group)
        # проверяю каждый объект post_objects, то что его группа
        # это группе group и не является группой group1
        for post in post_objects:
            with self.subTest():
                self.assertEqual(post.group, self.group)
                self.assertNotEqual(post.group, group1)

    def test_group_list_page_show_correct_contex(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-group'})
        )
        group_object = response.context['group']
        post_object = response.context['page_obj'][0]
        contex_page = {
            self.post.group: group_object,
            self.post.author: post_object.author,
            self.post.text: post_object.text,
            self.post.image: post_object.image,
            self.post.group.title: post_object.group.title,
            self.post.group.slug: post_object.group.slug,
            self.post.group.description: post_object.group.description
        }
        for expected, value in contex_page.items():
            with self.subTest():
                self.assertEqual(value, expected)

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'auth'})
        )
        author_object = response.context['post_author']
        first_object = response.context['page_obj'][0]
        contex_page = {
            self.post.author: author_object,
            self.post.author: first_object.author,
            self.post.text: first_object.text,
            self.post.image: first_object.image,
            self.post.group.title: first_object.group.title,
            self.post.group.slug: first_object.group.slug,
            self.post.group.description: first_object.group.description
        }
        for expected, value in contex_page.items():
            with self.subTest():
                self.assertEqual(value, expected)

    def test_post_detail_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': (f'{self.post.pk}')}
            )
        )
        post_object = response.context['post']
        expected = self.post
        self.assertEqual(post_object, expected)

    def test_post_create_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form = response.context.get('form')
        self.assertIsInstance(form, PostForm)
        is_edit = response.context['is_edit']
        self.assertEqual(is_edit, False)

    def test_post_edit_page_show_correct_context(self):
        test_post = Post.objects.create(
            author=self.user,
            text='Новый пост для проверки контекста'
        )
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': (f'{test_post.pk}')}
                    )
        )
        form = response.context.get('form')
        self.assertIsInstance(form, PostForm)
        is_edit = response.context['is_edit']
        self.assertEqual(is_edit, True)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Тестовое описание',
        )
        for i in range(1, 14):
            cls.posts = Post.objects.bulk_create([
                Post(
                    author=cls.user,
                    text=f'Тестовая запись {i}',
                    group=cls.group,
                )
            ])

    def setUp(self):
        self.user = User.objects.create_user(username='HasNoName')
        self.client = Client()
        cache.clear()

    def test_index_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_index_second_page_contains_three_records(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_list_first_page_contains_ten_records(self):
        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-group'})
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_list_second_page_contains_three_records(self):
        response = self.client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test-group'}
            ) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_profile_first_page_contains_ten_records(self):
        response = self.client.get(
            reverse('posts:profile', kwargs={'username': 'auth'})
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_second_page_contains_three_records(self):
        response = self.client.get(
            reverse(
                'posts:profile',
                kwargs={'username': 'auth'}
            ) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user1 = User.objects.create_user(username='auth1')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая запись 1',
        )
        cls.post1 = Post.objects.create(
            author=cls.user1,
            text='Тестовая запись 2',
        )

    def setUp(self):
        self.user = User.objects.get(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_follow_unfollow(self):
        """Проверка подписки и отписки"""
        count_follow = Follow.objects.count()
        response = self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={'username': 'auth'})
        )
        self.assertRedirects(
            response,
            reverse('posts:profile',
                    kwargs={'username': 'auth'}),
        )
        new_count_follow = Follow.objects.count()
        self.assertEqual(new_count_follow, count_follow + 1)
        response_1 = self.authorized_client.get(
            reverse('posts:profile_unfollow', kwargs={'username': 'auth'})
        )
        self.assertRedirects(
            response_1,
            reverse('posts:profile',
                    kwargs={'username': 'auth'}),
        )
        self.assertEqual(new_count_follow - 1, Follow.objects.count())

    def test_show_follow_(self):
        Follow.objects.create(
            user=self.user,
            author=self.user1
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        odj = response.context['page_obj'][0]
        self.assertEqual(odj, self.post1)
        self.assertNotEqual(odj, self.post)
