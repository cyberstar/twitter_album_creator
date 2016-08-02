# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Album, Image, AlbumImageRelation


class AlbumImageInline(admin.StackedInline):
    model = AlbumImageRelation
    extra = 1


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('name', 'images_count', )
    inlines = (AlbumImageInline, )

    def images_count(self, obj):
        return obj.images.count()
    images_count.short_description = 'Images count'


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    inlines = (AlbumImageInline, )
    fields = ('image_file', 'original_image_url', )
