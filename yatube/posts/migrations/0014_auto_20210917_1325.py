# Generated by Django 2.2.16 on 2021-09-17 10:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0013_auto_20210917_1300'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='pub_date',
            new_name='created',
        ),
    ]
