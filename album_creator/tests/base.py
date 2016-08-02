# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

from PIL import Image as PILImage
from PIL import ImageDraw as PILImageDraw

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.files import File
from ..models import Album, Image, AlbumImageRelation


def create_image(mode='RGB', size=(800, 600)):
    """
    Creates a simple in-memory image file.
    :param mode: PIL.Image mode, defaults to 'RGB'
    :param size: tuple image size in pixels
    :return:
    """
    image = PILImage.new(mode, size)
    draw = PILImageDraw.Draw(image)
    x_bit, y_bit = size[0] // 10, size[1] // 10
    draw.rectangle((x_bit, y_bit * 2, x_bit * 7, y_bit * 3), 'red')
    draw.rectangle((x_bit * 2, y_bit, x_bit * 3, y_bit * 8), 'red')
    return image


class AlbumNamesMixin(object):
    album1_name = 'python'
    album2_name = 'django'
    album3_name = 'html'

    def create_album(self, name):
        """
        Simple helper function for album creation.
        :param name: str album name
        :return: album_creator.models.Album instance
        """
        album_instance = Album(name=name)
        album_instance.save()
        return album_instance


class ImageHelperMixin(object):
    image_name = 'test_file.jpg'
    default_original_image_url = 'http://example.com/test_file.jpg'

    def create_image_file(self, image_name=None):
        """
        Creates dummy images and makes Django files from them.
        Make sure that you have defined class variable 'created_files' whicih
        should be a list, it will be used for clean up.
        :param image_name: str image name
        :return: django file
        """
        if image_name is None:
            image_name = self.image_name
        image = create_image()
        file_name = os.path.join(settings.FILE_UPLOAD_TEMP_DIR, image_name)
        image.save(file_name, 'JPEG')
        file = File(open(file_name, 'rb'), name=self.image_name)
        # store file path for clean up, test cases should define the class variable
        self.created_files.append(file_name)
        return file

    def delete_image_file(self, file_name):
        """
        Remove the file from file system. please be careful!
        :param file_name: str absolute path to the file
        :return: None
        """
        try:
            os.remove(file_name)
        except OSError:
            # seems that file was already removed
            pass

    def create_image(self, image_name=None, original_image_url=None):
        """
        Create an album_creator Image instance.
        :param image_name: str image name, if not provided the default will be used
        :param original_image_url: str original image url, if not provided the
        default will be used
        :return: album_creator.models.Image instance
        """
        if original_image_url is None:
            original_image_url = self.default_original_image_url

        image_file = self.create_image_file(image_name=image_name)
        # create album_creator Image
        image_instance = Image(
            image_file=image_file,
            original_image_url=original_image_url,
        )
        image_instance.save()
        return image_instance

    def tearDown(self):
        # clean up created files
        for created_file in self.created_files:
            self.delete_image_file(created_file)


class ImageRelationHelperMixin(AlbumNamesMixin, ImageHelperMixin):

    def setUp(self):
        self.album1 = self.create_album(self.album1_name)
        self.album2 = self.create_album(self.album2_name)

        self.image1 = self.create_image()
        self.image2 = self.create_image(
            image_name='test_image2.jpg',
            original_image_url='http://example.com/test_image2.jpg')

    def create_album_image_relation(self, album, image, tweet_id, tweet_url):
        """
        Creates an AlbumImageRelation
        :param album: album_creator.models.Album instance
        :param image: album_creator.models.Image instance
        :param tweet_id: int tweet id
        :param tweet_url: str tweet url
        :return: album_creator.models.AlbumImageRelation instance
        """
        relation = AlbumImageRelation(
            album=album,
            image=image,
            tweet_id=tweet_id,
            tweet_url=tweet_url,
        )
        relation.save()
        return relation


class UserHelperMixin(object):
    user_name = 'test_user'
    user_password = 'test_password'

    def setUp(self):
        # create a default user
        self.user = self.create_user()

    def create_user(self, user_name=None, password=None):
        """
        Creates a regular django user.
        :param user_name: str user name, if not provided defaults to self.user_name
        :param password: str password, if not provided defaults to self.user_password
        :return: django.contrib.auth.models User
        """
        if user_name is None:
            user_name = self.user_name
        if password is None:
            password = self.user_password
        user = User.objects.create(
            username=user_name,
            password=make_password(password),
        )
        return user
