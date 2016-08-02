# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import IntegrityError
from django.test import TestCase
from django.utils.encoding import force_text

from ..models import Album, Image, AlbumImageRelation

from .base import AlbumNamesMixin, ImageHelperMixin, ImageRelationHelperMixin


class AlbumTestCase(AlbumNamesMixin, TestCase):

    def test_album_craetion_and_str(self):
        # ensure that no album exists
        self.assertFalse(Album.objects.exists())
        album1 = self.create_album(name=self.album1_name)
        self.assertEqual(Album.objects.count(), 1)
        # ensure we don't fail with exception
        force_text(album1)

    def test_album_duplicate_names(self):
        self.assertFalse(Album.objects.exists())
        album1 = self.create_album(name=self.album1_name)
        self.assertEqual(Album.objects.count(), 1)

        with self.assertRaises(IntegrityError):
            album2 = Album.objects.create(name=self.album1_name)

    def test_get_absolute_url(self):
        album1 = self.create_album(self.album1_name)
        url = album1.get_absolute_url()
        # ensure that url has value
        self.assertFalse(url is None)
        self.assertGreater(len(url), 1)


class ImageTestCase(ImageHelperMixin, TestCase):
    # store created files paths here for tearDown
    # Note: Should be created on test class, not on the mixin
    created_files = []

    def test_image_creation_and_str(self):
        # ensure there are no images
        self.assertFalse(Image.objects.exists())
        image_instance = self.create_image()
        self.assertEqual(Image.objects.count(), 1)
        # ensure we don't fail with exception
        force_text(image_instance)

    def test_image_duplicate_by_url(self):
        # ensure there are no images
        self.assertFalse(Image.objects.exists())
        # create the default image
        image1_instance = self.create_image()
        # ensure image instance was created
        self.assertEqual(Image.objects.count(), 1)

        with self.assertRaises(IntegrityError):
            image2_instance = self.create_image(image_name='second_test_image.jpg')


class AlbumImageRelationTestCase(ImageRelationHelperMixin ,TestCase):
    created_files = []

    def test_image_relation_creation_and_str(self):
        # ensure there are no image relations
        self.assertFalse(AlbumImageRelation.objects.exists())
        relation = self.create_album_image_relation(
            album=self.album1,
            image=self.image1,
            tweet_id=111,
            tweet_url='http://twitter.com/test/statuses/111',
        )
        self.assertEqual(AlbumImageRelation.objects.count(), 1)
        force_text(relation)

    def test_unique_album_image(self):
        # ensure there are no image relations
        self.assertFalse(AlbumImageRelation.objects.exists())
        relation1 = self.create_album_image_relation(
            album=self.album1,
            image=self.image1,
            tweet_id=111,
            tweet_url='http://twitter.com/test/statuses/111',
        )
        self.assertEqual(AlbumImageRelation.objects.count(), 1)

        with self.assertRaises(IntegrityError):
            relation2 = self.create_album_image_relation(
                album=self.album1,
                image=self.image1,
                tweet_id=222,
                tweet_url='http://twitter.com/test/statuses/222',
            )
