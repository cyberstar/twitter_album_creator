# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.generics import ListAPIView

from ..models import Album
from .serializers import AlbumInfoSerializer


class AlbumListApiView(ListAPIView):
    queryset = Album.objects.all()
    serializer_class = AlbumInfoSerializer

