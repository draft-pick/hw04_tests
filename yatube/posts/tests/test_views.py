from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Post, Group

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="some_user")

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.templates_pages_obj = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user}):
                'posts/profile.html',
        }
        self.templates_pages = {
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}):
                'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}):
                'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        self.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }

    def post_checking(self, post):
        self.assertEqual(post.pk, self.post.pk)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group, self.post.group)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        template_pages_all = self.templates_pages_obj | self.templates_pages
        for reverse_name, template in template_pages_all.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_show_correct_context(self):
        """Шаблон index, group_list, profile
        сформирован с правильным контекстом.
        """

        for reverse_name in self.templates_pages_obj:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                post = response.context['page_obj'][0]
                self.post_checking(post)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""

        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        post = response.context['view_post']
        self.post_checking(post)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""

        response = self.authorized_client.get(
            reverse('posts:post_create')
        )
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""

        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        )
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_new_post(self):
        """Проверка нового поста на главной странице,
        на странице выбранной группы и в профайле пользователя."""

        post = Post.objects.create(
            author=self.user,
            text=self.post.text,
            group=self.group
        )
        for page in self.templates_pages_obj:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertIn(
                    post, response.context['page_obj']
                )

    def test_post_new_not_in_group(self):
        """Проверка поста в другой группе."""

        response = self.authorized_client.get(reverse('posts:index'))
        post = response.context['page_obj'][0]
        group = post.group
        self.assertEqual(group, self.group)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="some_user")
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group', )
        posts = [Post(
            text=f'Тестовый текст{i}',
            author=cls.user,
            group=cls.group) for i in range(13)]
        Post.objects.bulk_create(posts)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_paginator_index_group_list_profile(self):
        """Проверка пагинации на url: index, group_list, profile."""

        len_page = settings.PAGINATOR_POST_COUNT
        len_page_2 = Post.objects.count() - len_page
        paginator_context = {
            reverse('posts:index'): len_page,
            reverse('posts:index') + '?page=2': len_page_2,
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                len_page,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}) + '?page=2': len_page_2,
            reverse('posts:profile', kwargs={'username': self.user}):
                len_page,
            reverse('posts:profile',
                    kwargs={'username': self.user}) + '?page=2':
                len_page_2
        }
        for requested_page, page_len in paginator_context.items():
            with self.subTest(requested_page=requested_page):
                response = self.authorized_client.get(requested_page)
                self.assertEqual(len(response.context['page_obj']), page_len)