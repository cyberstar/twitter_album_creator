Project Overview
----------------
This project is a base setup for smart automatic album craetor application (``album_creator``).
This application allow you to create albums for hashtags, and then fetch the most recent images (photos) posted on Twitter for that hashtag since the last fetching.

Setup
-----
Since the app uses the Twitter API to search the photos, you need to create the file with access credentials.
This file should be named as ``default_twitter_credentials.json`` and contain the following: ::

    {"app_key": "<your_app_key>",
     "app_secret": "<your_app_secret>",
     "oauth_token": "<your_access_token>",
     "oauth_token_secret": "<your_access_token_secret>"}

After the credentials are in place follow this instruction:

#. Create the virtualenv for this project::

    virutalenv venv
    source venv/bin/activate

#. Install the requirements::

    pip install -r requirements.txt

#. Create/migrate the database::

    python manage.py migrate

#. Start the developement server::

    python manage.py runserver

Thats it! You can now access the app using your local host address (usually it is 127.0.0.1:8000 or localhost:8000)


Usage
-----

To create albums you need to be logged in, you can do it with django admin interface (there is a link in the top menu).
To create album you may use the create album link on the top menu or do it from admin interface.

After the album is created - navigate to the album details and hit the import button. After a while you will see new
imported photos and will get the email with updates.

REST API
^^^^^^^^
You can retrieve album names and urls to images with REST API by accessing the ``localhost:8000/api/album/`` url.
