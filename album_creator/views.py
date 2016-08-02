# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from operator import itemgetter

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, CreateView, View

from .models import Album, AlbumImageRelation
from .helpers import import_photos_for_album, send_email_notifications
from .utils import get_credentials_from_file, get_twitter_api


class AlbumsListView(ListView):
    model = Album
    template_name = 'album_creator/album_list.html'


class CreateAlbumView(LoginRequiredMixin, CreateView):
    model = Album
    fields = ('name',)
    template_name = 'album_creator/create_album.html'

    def get_success_url(self):
        return reverse('album-detail', kwargs={'album_name': self.object.name})


class AlbumImagesView(ListView):
    model = AlbumImageRelation
    template_name = 'album_creator/album_images.html'

    def get_queryset(self):
        qs = super(AlbumImagesView, self).get_queryset()
        # get the correct album
        album_name = self.kwargs.get('album_name')
        album = get_object_or_404(Album, name=album_name)
        qs = qs.filter(album=album).select_related('image')
        return qs

    def get_context_data(self, **kwargs):
        user = self.request.user
        # check if user is authenticated, if he is - he can update
        # the album and request the fetch/import from twitter
        kwargs['user_can_import'] = user.is_authenticated()
        kwargs['album_name'] = self.kwargs.get('album_name')
        return super(AlbumImagesView, self).get_context_data(**kwargs)


class AlbumImportView(LoginRequiredMixin, View):
    http_method_names = ('get',)
    permission_denied_message = 'Sorry, you have no permissions to do that.,,'
    raise_exception = True
    email_subject_template_name = 'album_creator/emails/import_notification.subject.txt'
    email_body_template_name = 'album_creator/emails/import_notification.body.txt'
    from_email = settings.DEFAULT_FROM_EMAIL

    def get_success_url(self):
        return reverse('album-detail', kwargs={'album_name': self.album_name})

    def get(self, request, *args, **kwargs):
        album_name = kwargs.get('album_name')
        # if there is no such album - return 404
        if album_name is None:
            raise Http404()
        # album name will be used in get_success_url
        self.album_name = album_name

        # if this setting is not set - fail with 500 error
        credentials_file_paht = settings.TWITTER_CREDENTIALS_JSON_FILE
        twitter_credentials = get_credentials_from_file(credentials_file_paht)
        twitter_api = get_twitter_api(twitter_credentials)
        imported_photos_pks = import_photos_for_album(
            api=twitter_api, album_name=album_name, limit=100)

        # if there were new photos imported - send email notifications
        if imported_photos_pks:
            # extract email from MANAGERS tuple
            email_getter = itemgetter(1)
            managers_emails = list(map(email_getter, settings.MANAGERS))
            # send notifications
            send_email_notifications(
                subject_template_name=self.email_subject_template_name,
                body_template_name=self.email_body_template_name,
                album_name=album_name,
                photo_pks_list=imported_photos_pks,
                from_email=self.from_email,
                recipients=managers_emails,
            )

        return HttpResponseRedirect(self.get_success_url())