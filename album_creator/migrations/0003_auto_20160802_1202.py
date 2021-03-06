# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-02 12:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('album_creator', '0002_albumimagerelation_imported_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='name',
            field=models.CharField(help_text='Hash tag without the "#" sign, will be used to fetch photos from twitter', max_length=140, unique=True, verbose_name='Album name'),
        ),
    ]
