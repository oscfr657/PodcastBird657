# Generated by Django 3.2.11 on 2022-01-22 22:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('podcastbird657', '0004_auto_20211114_1706'),
    ]

    operations = [
        migrations.RenameField(
            model_name='podcastbirdpage',
            old_name='show_coverImage',
            new_name='show_cover',
        ),
        migrations.RenameField(
            model_name='podepisodebirdpage',
            old_name='show_coverImage',
            new_name='show_cover',
        ),
    ]
