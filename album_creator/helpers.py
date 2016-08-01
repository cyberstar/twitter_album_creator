# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.core.mail import send_mass_mail
from django.template.loader import render_to_string
from django.contrib.sites.models import Site

from .models import Album, AlbumImageRelation, Image
from .utils import (
    search_tweets_by_hashtag, get_image_url_from_tweet,
    get_tweet_id, get_tweet_url, get_image_from_url,
)

# todo: consider helpful logger naming
logger = logging.getLogger(__name__)


def import_photo_from_tweet(tweet, album_instance):
    """
    Import a single photo from a single tweet data (received with twitter api).
    :param tweet: dict tweet data.
    :param album_instance: .models.Album instance
    :return: int or None, None if nothing was imported, image_instance.pk in case of
    successful import
    """
    tweet_id = get_tweet_id(tweet)
    tweet_url = get_tweet_url(tweet)
    image_url = get_image_url_from_tweet(tweet)

    # check that we have image url
    if image_url is None:
        logger.debug('Skipping: No image_url found for tweet {}'.format(tweet_url))
        return None

    # validate uniqueness
    album_image_relation = AlbumImageRelation.objects.filter(album=album_instance, image__image_url=image_url)
    if album_image_relation.exists():
        logger.debug('Skipping duplicate image entry for tweet {}'.format(tweet_url))
        return None
    # check if we need to fetch an image
    try:
        image_instance = Image.objects.get(image_url=image_url)
        logger.debug(
            'Found existing Image  in the database, (pk={}, url={} '.format(
                image_instance.id, image_url))
    except Image.DoesNotExist:
        image_instance = None
    # if there is no previously imported image - create one
    if image_instance is None:
        logger.debug('Fetching the image file from url {}'.format(image_url))
        image_django_file = get_image_from_url(image_url)
        logger.debug('Creating new Image entry for url {}'.format(image_url))
        image_instance = Image.objects.create(image_file=image_django_file,
                                              image_url=image_url)
    logger.debug('Creating new Album to Image relation for tweet: {}'.format(tweet_url))
    album_instance.image_relations.create(
        image=image_instance,
        tweet_id=tweet_id,
        tweet_url=tweet_url)
    return image_instance.pk


def import_photos_for_album(api, album_name, limit=100):
    """
    Imports photos from twitter by searching tweets with hash tag that is the
    same as album name. This function will search twitter, fetch photos and create
    corresponding entries in the database and notify the managers and the admin
    with import results.
    :param api: Twython instance, twitter api connection
    :param album_name: str album name - the hash tag without the '#' symbol
    :param limit: int limit twitter search results
    :return: int number of imported photos
    """
    logger.info('Starting import for album name "{}"'.format(album_name))
    try:
        logger.debug('Getting the album instance by name')
        album_instance = Album.objects.get(name=album_name)
    except Album.DoesNotExist as e:
        logger.error(
            'No album insatnce found in the database for name {}'.format(album_name))
        return -1
    hash_tag = '#{}'.format(album_name)
    # check if there were previous imports, in case there are - we only
    # need the most latest tweet id.
    # Also limit the query to 1 record, and only tweet_id field.
    last_imported_tweet_id_for_album = (
        album_instance.image_relations
                      .all()
                      .order_by('-tweet_id')
                      .values_list('tweet_id')[:1])
    if last_imported_tweet_id_for_album:
        # if there were previous imports - use appropriate twitter id
        last_imported_tweet_id = last_imported_tweet_id_for_album[0][0]
        logger.debug(
            'Found last imported tweet_id from previous import: {}'.format(
                last_imported_tweet_id))
    else:
        logger.debug(
            'No previous imports found for album {}'.format(
                album_name))
        last_imported_tweet_id = None
    logger.debug(
        'search_tweets_by_hashtag.\n'
        '\thash tag: {hash_tag}\n'
        '\tlimit: {limit}\n'
        '\tsince_id: {since_id}\n'
        '\timage_only: {image_only}'.format(
            hash_tag=hash_tag,
            limit=limit,
            since_id=last_imported_tweet_id,
            image_only=True
        ))
    search_results = search_tweets_by_hashtag(
        api=api,
        hash_tag=hash_tag,
        limit=limit,
        since_id=last_imported_tweet_id,
        image_only=True
    )
    logger.debug('Got {} search results after the query'.format(
        len(search_results)))

    # Process the search results
    successful_imports_pks = []
    for tweet in search_results:
        image_pk = import_photo_from_tweet(tweet, album_instance=album_instance)
        if image_pk is not None:
            successful_imports_pks.append(image_pk)

    logger.debug('Successfully imported {} photo(s)'.format(
        len(successful_imports_pks)))
    logger.debug('Imported photos pks: \n{}'.format(
        '\n'.join(str(pk) for pk in successful_imports_pks)
    ))
    return successful_imports_pks


def construct_notification_emails(subject_template_name, body_template_name,
                                  album_name, photo_pks_list, from_email,
                                  recipients):
    """
    Construct email messages to notify recipients about import results.
    :param subject_template_name: str path to subject template
    :param body_template_name: str path to body template
    :param album_name: str name of the album, will be refrlected in the subject
    :param photo_pks_list: list of photo pks to build urls
    :param from_email: str email address to be used in from_email field
    :param recipients: str recipients
    :return: list of tuples suitable for usage in send_mass_email
    """
    photos = Image.objects.filter(pk__in=photo_pks_list)
    album = Album.objects.get(name=album_name)
    site = Site.objects.get_current()
    context_dict = {
        'photos': photos,
        'album_name': album_name,
        'album_total_photos_count': album.images.count(),
        'number_of_photos': len(photos),
        'album_url': 'http://{}{}'.format(site.domain,
                                          album.get_absolute_url()),
    }
    subject = render_to_string(subject_template_name, context=context_dict)
    # clean the subject, must be one line
    subject = subject.replace('\n', '').replace('\r', '').strip()
    body = render_to_string(body_template_name, context_dict)
    prepared_data = [(subject, body, from_email, (to_email,)) for to_email in recipients]
    return prepared_data


def send_email_notifications(subject_template_name, body_template_name,
                             album_name, photo_pks_list, from_email, recipients):
    """
    Constructs and sends import email notifications to recipients.
    :param subject_template_name: str path to subject template
    :param body_template_name: str path to body template
    :param album_name: str name of the album, will be refrlected in the subject
    :param photo_pks_list: list of photo pks to build urls
    :param from_email: str email address to be used in from_email field
    :param recipients: str recipients
    :return: number of sent emails
    """
    data = construct_notification_emails(
        subject_template_name=subject_template_name,
        body_template_name=body_template_name,
        album_name=album_name,
        photo_pks_list=photo_pks_list,
        from_email=from_email,
        recipients=recipients,
    )
    return send_mass_mail(data)
