# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.test import TestCase


from ..models import Album, Image, AlbumImageRelation

from .base import (
    AlbumNamesMixin, ImageHelperMixin, ImageRelationHelperMixin,
    UserHelperMixin,
)


class GetViewUrlHelperMixin(object):

    def get_view_url(self, kwargs):
        """
        Reverses the url to the view by view name.
        To work properly class should have 'view_name' class variable
        :return: str url address
        """
        return reverse(self.view_name, kwargs=kwargs)

    def setUp(self):
        super(GetViewUrlHelperMixin, self).setUp()
        if hasattr(self, 'get_view_kwargs'):
            kwargs = self.get_view_kwargs()
        else:
            kwargs = {}
        self.view_url = self.get_view_url(kwargs)


class AlbumsListViewTestCase(GetViewUrlHelperMixin,
                             ImageRelationHelperMixin,
                             TestCase):
    view_name = 'album-list'
    created_files = []

    def test_no_albums(self):
        # remove the album that was created in ImageRelationHelperMixin
        Album.objects.all().delete()
        response = self.client.get(self.view_url)
        self.assertEqual(response.status_code, 200)

    def test_with_empty_album(self):
        response = self.client.get(self.view_url)
        self.assertContains(response, self.album1_name)

    def test_with_non_empty_album(self):
        relation1 = self.create_album_image_relation(
            album=self.album1,
            image=self.image1,
            tweet_id=111,
            tweet_url='http://twitter.com/test/statuses/111',
        )
        response = self.client.get(self.view_url)
        self.assertContains(response, self.album1_name)


class CreateAlbumViewTestCase(GetViewUrlHelperMixin,
                              UserHelperMixin,
                              TestCase):
    view_name = 'album-create'

    def test_requires_login(self):
        response = self.client.get(self.view_url)
        # ensure we're not allowing anyone to create albums
        self.assertEqual(response.status_code, 302)

    def test_album_creation_get(self):
        self.client.login(username=self.user_name,
                          password=self.user_password)
        response = self.client.get(self.view_url)
        # check that response status code is 200 and that it
        # contains the page title
        self.assertContains(response, 'Create new album')

    def test_album_creation_post(self):
        self.client.login(username=self.user_name,
                          password=self.user_password)
        data = {
            'name': 'testalbum'
        }
        self.assertEqual(Album.objects.count(), 0)
        response = self.client.post(self.view_url, data=data)
        # ensure album was created
        self.assertEqual(Album.objects.count(), 1)
        # ensure that the name is correct
        self.assertEqual(Album.objects.get().name, data['name'])

    def test_album_creation_post_requires_login(self):
        data = {
            'name': 'testalbum'
        }
        self.assertEqual(Album.objects.count(), 0)
        response = self.client.post(self.view_url, data=data)
        self.assertEqual(response.status_code, 302)
        # ensure that album was not created
        self.assertEqual(Album.objects.count(), 0)


class AlbumImagesViewTestCase(GetViewUrlHelperMixin,
                              ImageRelationHelperMixin,
                              TestCase):
    view_name = 'album-detail'
    created_files = []

    def get_view_kwargs(self):
        return {'album_name': self.album1_name}

    def test_get_does_not_requires_login(self):
        response = self.client.get(self.view_url)
        # ensure that the default album name is displayed on
        # the page, the album is created in ImageRelationHelperMixin
        self.assertContains(response, self.album1_name)

    def test_view_renders_images_and_links(self):
        tweet_url = 'http://twitter.com/test/statuses/111'
        relation1 = self.create_album_image_relation(
            album=self.album1,
            image=self.image1,
            tweet_id=111,
            tweet_url=tweet_url,
        )
        response = self.client.get(self.view_url)
        self.assertContains(response, tweet_url)
        self.assertContains(response, self.image1.image_file.url)


class AlbumImportViewTestCase(GetViewUrlHelperMixin,
                              ImageRelationHelperMixin,
                              TestCase):
    created_files = []
    view_name = 'album-import-photos'

    def get_view_kwargs(self):
        return {'album_name': self.album1_name}

    def test_import_requires_login(self):
        album1_images_count = self.album1.images.count()
        response = self.client.get(self.view_url)
        self.assertEqual(response.status_code, 403)
        # ensure nothing has been imported (this might be the case
        # when test credentials exist
        self.assertEqual(self.album1.images.count(),
                         album1_images_count)
