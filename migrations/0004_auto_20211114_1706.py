# Generated by Django 3.2.8 on 2021-11-14 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('podcastbird657', '0003_auto_20211113_1659'),
    ]

    operations = [
        migrations.AddField(
            model_name='podcastbirdpage',
            name='explicit',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='podepisodebirdpage',
            name='explicit',
            field=models.BooleanField(default=False),
        ),
    ]
