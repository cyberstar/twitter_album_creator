# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from twython import Twython
import requests

from cStringIO import StringIO
from django.core.files import File

# will be used to build tweet absolute url
TWEET_URL_TEMPLATE = "https://twitter.com/{user_name}/status/{tweet_id}/"


def get_credentials_from_file(file_path):
    """
    Returns a dict with twitter api credentials. Reads them from json file.
    :param file_path: str absolute path to credentials file
    :return: dict with credentials
    """
    # since this operation requires disk access it can be optimized
    # with cache/memoization, should not be an issue for small projects
    with open(file_path, 'rb') as credentials_file:
        return json.load(credentials_file)


def get_twitter_api(credentials):
    """
    Returns authenticated api to twitter.
    :param credentials: dict with credentials, expected to be as following:
        'app_key' - Consumer Key (API Key)
        'app_secret' - Consumer Secret (API Secret)
        'oauth_token' - Access Token
        'oauth_token_secret' - Access Token Secret
    based on Twitter Keys and Access tokens settings for an app
    :return: twython.Twython
    """
    twitter = Twython(**credentials)
    # twitter = Twython(app_key=credentials['consumer_key'],
    #                   app_secret=credentials['consumer_secret'],
    #                   oauth_token=credentials['access_token'],
    #                   oauth_token_secret=credentials['access_token_secret'])
    return twitter


def get_image_from_url(image_url):
    """
    Fetch the image from original_image_url and return Django file object.
    :param image_url: str absolute url to image
    :return: django.core.files.File
    """
    response = requests.get(image_url)
    file_name = image_url.split('/')[-1]
    file_like = StringIO(response.content)
    file_obj = File(file_like, name=file_name)
    return file_obj


def get_original_image_url_from_tweet(tweet):
    """
    Extracts the tweet photo image url from tweet data.
    :param tweet: dict of the tweet provided by twitter API
    :return: str original image url or None in case if something went wrong
    """
    entities = tweet.get('entities', {})
    media_entities = entities.get('media', [])
    image_url = None
    # media_entities is a list, iterate until we meet the type 'photo'
    for media in media_entities:
        if media.get('type') == 'photo':
            image_url = media.get('media_url')
            break
    return image_url


def get_tweet_id(tweet):
    """
    Extracts tweet id from tweet data received with twitter api.
    :param tweet: dict with tweet data
    :return: int tweet id
    """
    return tweet.get('id')


def get_tweet_url(tweet):
    """
    Builds tweet absolute url from tweet data received with twitter api.
    :param tweet: dict with tweet data
    :return: str tweet url
    """
    user_info = tweet.get('user')
    user_screen_name = user_info.get('screen_name')
    tweet_id = get_tweet_id(tweet)
    return TWEET_URL_TEMPLATE.format(user_name=user_screen_name,
                                     tweet_id=tweet_id)


def search_tweets_by_hashtag(api, hash_tag, limit=100, since_id=None, image_only=True):
    """
    Search twitter for tweets with specific hashtag, if image_only is true - will search
    for tweets that have photos in it (twitter filtering).
    :param api: twython api to access twitter (should be authenticated)
    :param hash_tag: str hash tag for search
    :param limit: int limit results to this number
    :param since_id: int tweet id, perform search only on tweets that are older then this id
    :param image_only: bool only search tweets with images
    :return: dict with statuses .
    """
    # build the query to twitter, search for hashtag in any case, if image_only selected - add
    # twitter filtering to the query based on twitter api documentation
    # https://dev.twitter.com/rest/public/search (query operators)
    query = '{hash_tag}{extra}'.format(
        hash_tag=hash_tag,
        extra=' filter:images' if image_only else '')
    search_kwargs = {
        'q': query,
        'count': limit,
    }
    # limit the search with only recent items
    if since_id:
        search_kwargs['since_id'] = since_id
    # query the api
    search_results = api.search(**search_kwargs)
    # search results will be a dict of 'search_metadata' and 'statuses', where statuses
    # are actual twitter statuses (dict)
    return search_results['statuses']
