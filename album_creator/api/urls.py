# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from .views import AlbumListApiView


urlpatterns = [
    url(r'^$', AlbumListApiView.as_view(), name='album-list'),
]