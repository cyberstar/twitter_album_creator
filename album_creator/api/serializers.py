# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers
from ..models import Album, Image, AlbumImageRelation


class ImageInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = ('image_file', 'original_image_url',)


class ImageRelationInfoSerializer(serializers.ModelSerializer):
    image = ImageInfoSerializer()

    class Meta:
        model = AlbumImageRelation
        fields = ('image', 'tweet_url',)


class AlbumInfoSerializer(serializers.ModelSerializer):
    images = ImageInfoSerializer(many=True)

    class Meta:
        model = Album
        fields = ('name', 'images',)
