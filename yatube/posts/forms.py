from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {'text': 'Текст поста', 'group': 'Группа'}
        help_texts = {'text': 'Введите текст', 'group': 'Введите группу'}


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': 'Комментарий'}
        help_texts = {'text': 'Оставьте комментарий'}
