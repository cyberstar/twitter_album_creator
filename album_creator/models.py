# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.encoding import python_2_unicode_compatible, force_text


@python_2_unicode_compatible
class Album(models.Model):
    name = models.CharField(
        verbose_name='Album name',
        max_length=140,
        help_text=(
            'Hash tag without the "#" sign, will be used to fetch photos '
            'from twitter'),
    )
    images = models.ManyToManyField(
        to='Image',
        related_name='albums',
        through='AlbumImageRelation',
    )

    def __str__(self):
        return force_text(self.name)

    def get_absolute_url(self):
        return reverse('album-detail', kwargs={'album_name': self.name})


@python_2_unicode_compatible
class Image(models.Model):
    """
    Image that is fetched from tweet for a specific hash tag (album).
    Keeps track of the original image url to awoid duplicates.
    """
    image_file = models.ImageField(
        verbose_name='Image',
        help_text='Fetched image file',
        upload_to='uploads/',
    )
    original_image_url = models.URLField(
        verbose_name='Original image url',
        unique=True,
    )

    def __str__(self):
        return force_text(self.original_image_url)


@python_2_unicode_compatible
class AlbumImageRelation(models.Model):
    """
    Relation between Album and Image, since one image can belong to multiple albums.
    Keeps track of the tweet and the status of notification.
    """
    album = models.ForeignKey(
        to='Album',
        related_name='image_relations',
    )
    image = models.ForeignKey(
        to='Image',
        related_name='album_relations',
    )
    tweet_id = models.BigIntegerField(
        verbose_name='Tweet ID',
        help_text='Used to track last imported photos',

    )
    tweet_url = models.URLField(
        verbose_name='Tweet url',
        help_text='Tweet url were the image appeared',
    )
    imported_at = models.DateTimeField(
        verbose_name='Image import datetime',
        auto_now_add=True,
    )

    def __str__(self):
        return force_text(self.pk)

    class Meta:
        unique_together = (('album', 'image'),)
