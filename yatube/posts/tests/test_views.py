from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Follow, Group, Post
from yatube.settings import PAGE_COUNTER

User = get_user_model()


class PostVIEWSTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Username')
        cls.user_n = User.objects.create_user(username='auth2')
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client_2 = Client()
        cls.authorized_client_2.force_login(cls.user_n)
        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
            description='Тестовое описание',
        )
        cls.test_post = Post.objects.create(
            text='text',
            author=cls.user,
            group=cls.test_group,
        )

        PostVIEWSTests == cls
        cls.post_list = []
        for i in range(15):
            test_create_post = Post.objects.create(
                text=f'Test post {i}.', author=cls.user, group=cls.test_group)
            cls.post_list.append(test_create_post)

        cls.index = reverse('posts:index')
        cls.group_list = reverse(
            'posts:group_list',
            kwargs={'slug': PostVIEWSTests.test_group.slug})
        cls.profile = reverse(
            'posts:profile',
            kwargs={'username': PostVIEWSTests.user.username})
        cls.post_detail = reverse(
            'posts:post_detail',
            kwargs={'post_id': cls.post_list[0].id})
        cls.post_edit = reverse(
            'posts:post_edit',
            kwargs={'post_id': cls.post_list[0].id})
        cls.post_create = reverse('posts:post_create')
        cls.profile_follow = reverse(
            'posts:profile_follow',
            kwargs={'username': cls.user})
        cls.profile_unfollow = reverse(
            'posts:profile_unfollow',
            kwargs={'username': cls.user})
        cls.follow_index = reverse('posts:follow_index')

        cls.templates_page_names = {
            cls.index: 'posts/index.html',
            cls.group_list: 'posts/group_list.html',
            cls.profile: 'posts/profile.html',
            cls.post_detail: 'posts/post_detail.html',
            cls.post_edit: 'posts/create_post.html',
            cls.post_create: 'posts/create_post.html',
        }

    def setUp(self):
        cache.clear()

    def test_pages_uses_correct_template(self):
        for reverse_name, template in self.templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_correct_context(self):
        response_index = self.guest_client.get(self.index)
        test_post = response_index.context['page_obj']
        for post in test_post:
            with self.subTest(post=post):
                get_post = Post.objects.get(id=post.id)
                self.assertEqual(post.text, get_post.text)
                self.assertEqual(post.author, get_post.author)
                self.assertEqual(
                    len(response_index.context['page_obj']),
                    10,
                    PAGE_COUNTER)
        second_response_index = self.client.get(
            reverse(
                'posts:index') + '?page=2')
        self.assertEqual(
            len(second_response_index.context['page_obj']), 6,
            Post.objects.all().count() - PAGE_COUNTER)

    def test_group_list_correct_context(self):
        response_group_list = self.guest_client.get(self.group_list)
        test_post = response_group_list.context['page_obj']
        group = self.test_group
        self.assertEqual(
            len(response_group_list.context['page_obj']),
            10,
            PAGE_COUNTER)
        second_response_group_list = self.client.get(
            reverse('posts:index') + '?page=2')
        self.assertEqual(
            len(second_response_group_list.context['page_obj']), 6,
            Post.objects.all().count() - PAGE_COUNTER)
        for post in test_post:
            with self.subTest(post=post):
                checked_post = Post.objects.get(id=post.id)
                self.assertEqual(post.text, checked_post.text)
                self.assertEqual(post.author, checked_post.author)
                self.assertEqual(post.group, group)

    def test_profile_correct_context(self):
        response_profile = self.guest_client.get(self.profile)
        test_posts = response_profile.context['page_obj']
        post_count = response_profile.context['post_count']
        self.assertEqual(
            len(response_profile.context['page_obj']), 10,
            PAGE_COUNTER)
        second_response_profile = self.client.get(
            reverse('posts:index') + '?page=2')
        self.assertEqual(
            len(second_response_profile.context['page_obj']), 6,
            Post.objects.all().count() - PAGE_COUNTER)
        for post in test_posts:
            with self.subTest(post=post):
                create_post = Post.objects.get(id=post.id)
                create_post_count = create_post.author.posts.all().count()
                create_author = self.user
                self.assertEqual(post.text, create_post.text)
                self.assertEqual(post.author, create_author)
                self.assertEqual(create_post_count, post_count)

    def test_post_detail_correct_context(self):
        response_post_detail = self.guest_client.get(self.post_detail)
        test_post = response_post_detail.context['post']
        test_post_count = response_post_detail.context['post_count']
        correct_post = Post.objects.get(id=test_post.id)
        correct_post_count = test_post.author.posts.all().count()
        self.assertEqual(test_post.text, correct_post.text)
        self.assertEqual(correct_post_count, test_post_count)

    def test_post_edit_correct_context(self):
        response = PostVIEWSTests.authorized_client.get(self.post_edit)
        post_user = response.context['user']
        post_author = Post.objects.get(id=self.post_list[0].id).author
        self.assertEqual(post_user, post_author)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get(
                    'form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_correct_context(self):
        response = PostVIEWSTests.authorized_client.get(self.post_create)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get(
                    'form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_cache_index_page(self):
        first_post = Post.objects.get(pk=self.post_list[14].id)
        first_response = self.guest_client.get(self.index).content
        first_post.delete()
        second_response = self.guest_client.get(self.index).content
        self.assertEqual(first_response, second_response)

    def test_follow(self):
        response_follow = Follow.objects.count()
        response = self.authorized_client_2.get(self.profile_follow)
        data = Follow.objects.get(user=self.user_n, author=self.user)
        self.assertTrue(data, response)
        self.assertRedirects(response, self.profile)
        self.assertEqual(Follow.objects.count(), response_follow + 1)
        
    def test_unfollow(self):
        response_unfollow = Follow.objects.count()
        response = self.authorized_client_2.get(self.profile_unfollow)
        self.assertRedirects(response, self.profile)
        self.assertEqual(Follow.objects.count(), response_unfollow)

    def test_follow_index(self):
        response_context = self.authorized_client.get(self.follow_index)
        post = response_context.context['page_obj']
        self.assertTrue(Post.objects.get(
            text=self.test_post.text),
            post
        )
        response_2 = self.authorized_client_2.get(self.follow_index)
        post_2 = response_2.context['page_obj']
        self.assertNotEqual(post_2, Post.objects.get(
            text=self.test_post.text))
