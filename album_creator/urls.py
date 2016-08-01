# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from .views import (
    CreateAlbumView, AlbumsListView, AlbumImagesView, AlbumImportView,
)

urlpatterns = [
    url(r'^$', AlbumsListView.as_view(),
        name='album-list'),
    url(r'^album/create/', CreateAlbumView.as_view(),
        name='album-create'),
    url(r'^album/(?P<album_name>[a-zA-Z]+)/$', AlbumImagesView.as_view(),
        name='album-detail'),
    url(r'^album/(?P<album_name>[a-zA-Z]+)/import/$', AlbumImportView.as_view(),
        name='album-import-photos'),
]
