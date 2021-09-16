import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()
        cls.user = User.objects.create_user(username='Username')
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.test_group = Group.objects.create(
            title='test title',
            slug='test-slug',
            description='Test desc',
        )
        cls.test_post = Post.objects.create(
            author=cls.user,
            text='Test text',
            group=cls.test_group,
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.image_adress = 'posts/small.gif'
        cls.test_comment = Post.objects.create(
            text='Test comment',
            author=cls.user,
            group=cls.test_group
        )
        cls.test_comment_data = {
            'text': 'Test comment',
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def check_post_create(self):
        form_data = {
            'text': PostFormTests.test_post.text,
            'group': PostFormTests.test_group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.author.username}))
        self.assertTrue(
            Post.objects.filter(
                author=self.user.author,
                text=PostFormTests.test_post.text,
                group=PostFormTests.group.pk,).exists())

    def test_post_create(self):
        post_id = PostFormTests.test_post.pk
        form_data = {
            'text': PostFormTests.test_post.text,
            'group': PostFormTests.test_group.pk,
        }
        response_author = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': post_id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response_author,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': post_id}))
        PostFormTests.test_post.refresh_from_db()
        self.assertEqual(
            PostFormTests.test_post.text,
            form_data['text'])
        self.assertEqual(
            PostFormTests.test_post.group.pk,
            form_data['group'])

    def test_image(self):
        form_data = {
            'text': PostFormTests.test_post.text,
            'group': PostFormTests.test_group.pk,
            'image': PostFormTests.image,
        }
        post_image = self.authorized_client.post(
            reverse('post:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            post_image,
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username})
        )
        PostFormTests.test_post.refresh_from_db()
        self.assertEqual(
            PostFormTests.test_post.text,
            form_data['text']
        )

    def test_post_comment(self):
        post_comment = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.test_comment.pk}
            ),
            data=self.test_comment_data,
            follow=True
        )
        self.assertRedirects(
            post_comment,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.test_comment.pk}
            )
        )
        PostFormTests.test_post.refresh_from_db()
        self.assertEqual(
            PostFormTests.test_comment.text,
            self.test_comment_data['text']
        )
