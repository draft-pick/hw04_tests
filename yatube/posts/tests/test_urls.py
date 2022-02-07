from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='HasNoName')
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.templates_url_guest_client_url = {
            '/': 'posts/index.html',
            f'/group/{PostURLTests.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
        }
        self.templates_url_authorized_client_url = {
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }

    def test_url_guest_user(self):
        """Страницы, доступные всем пользователям."""

        for url in self.templates_url_guest_client_url:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_authorized_client(self):
        """Страницы в словаре доступны авторизованному пользователю."""

        for url in self.templates_url_guest_client_url:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_404(self):
        """Запрос к несуществующей странице вернёт ошибку 404."""

        response = self.client.get('/some_page_404/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_guest_client_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        for address, template in self.templates_url_guest_client_url.items():
            with self.subTest(address=address):
                response = self.client.get(address, follow=True)
                self.assertTemplateUsed(response, template)

    def test_urls_authorized_client_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        for address, template in (
                self.templates_url_authorized_client_url.items()
        ):
            with self.subTest(address=address):
                response = self.authorized_client.get(address, follow=True)
                self.assertTemplateUsed(response, template)
