from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Username')
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            description='Те,стовое описание',
            slug='test_slug'
        )
        cls.test_post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
        )
        cls.status_code_url = {
            '/': HTTPStatus.OK,
            f'/group/{cls.test_group.slug}/': HTTPStatus.OK,
            f'/profile/{cls.user.username}/': HTTPStatus.OK,
            f'/posts/{cls.test_post.pk}/': HTTPStatus.OK,
        }

    def test_urls_ctatus_code_200(self):
        for adress, code in self.status_code_url.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, code)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            '/404/': 'core/404.html',
            '/': 'posts/index.html',
            f'/group/{self.test_group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.test_post.pk}/edit/': 'posts/create_post.html',
            f'/posts/{self.test_post.pk}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
        }
        for template, adress in templates_url_names.items():
            cache.clear()
            with self.subTest(adress=adress):
                response = self.authorized_client.get(template)
                self.assertTemplateUsed(response, adress)

    def test_page_404(self):
        response = self.guest_client.get('/404/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_unexpecting_page_url_exists_at_desired_location(self):
        response = self.authorized_client.get('/test_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_id_edit_url_exists_at_desired_location(self):
        response = self.authorized_client.get(
            f'/posts/{self.test_post.pk}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url_redirect_anonymous_on_admin_login(self):
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(response, ('/auth/login/?next=/create/'))
