


Celery on OSX for Development
==============================

1. Install redis-server

    1. Download redis from http://redis.io/

    2. Extract and run make

        ```
        make
        ```

    3. Copy excutable files

        ```
        sudo cp src/redis-server /usr/local/bin/
        sudo cp src/redis-cli /usr/local/bin/
        ```

2. Install Celery package with Django and Redis support from http://pypi.python.org/pypi/django-celery-with-redis/

    ```
    python setup.py build
    sudo python setup.py install
    ```

3. Follow the steps from http://django-celery.readthedocs.org/en/latest/getting-started/first-steps-with-django.html

4. Run command

    ```
    $ redis-server
    $ python manage.py celeryd -l info
    ```

3rd Library + Resources
==============================
https://github.com/dcramer/django-sentry
https://github.com/dcramer/nexus
https://github.com/django-debug-toolbar/django-debug-toolbar
http://pypi.python.org/pypi/django-maintenancemode
http://djangopackages.com/packages/p/django-pagination/ or https://github.com/dcramer/django-paging
https://github.com/etianen/django-reversion

REST
https://github.com/tomchristie/django-rest-framework
https://github.com/toastdriven/django-tastypie

SSL
http://stackoverflow.com/questions/2131727/django-and-ssl-question
http://www.redrobotstudios.com/blog/2009/02/18/securing-django-with-ssl/
https://www.rapidsslonline.com/

PDF Thumbnails Generator
http://www.cyberciti.biz/tips/howto-linux-creating-a-image-thumbnails-from-shell-prompt.html#comment-19317
http://www.imagemagick.org/script/index.php
http://linux.die.net/man/1/thumbpdf
http://stackoverflow.com/questions/5328401/efficient-thumbnail-generation-of-huge-pdf-file
http://blog.prashanthellina.com/2008/02/03/create-pdf-thumbnails-using-imagemagick-on-linux/

Online PDF
http://www.flipsnack.com/

Document Thumbnails
==============================

- Use OpenOffice headless to convert document or create thumbnail
- FFmpeg
http://blog.prashanthellina.com/2008/03/29/creating-video-thumbnails-using-ffmpeg/


Security Scheme
==============================

Prevent from
- Man in the middle
- Extract resources from device
- Send request directly from browser, not from a device

Read this
http://stackoverflow.com/questions/7262299/json-reject-server-requests-from-third-parties
http://en.wikipedia.org/wiki/Public-key_cryptography
http://en.wikipedia.org/wiki/Diffie%E2%80%93Hellman_key_exchange

Register iPad app
1. User input account information (Sign Up/Sign In)
2. Generate a unique id for a device
   (https://github.com/gekitz/UIDevice-with-UniqueIdentifier-for-iOS-5)
3. Generate a pair of public/private key, store the private key to Keychain
4. Send the account information, the device id, and the public key to server via HTTPS
5. Server will check if the device key is already registered, if not,
   then add to the user's devices list. (Also limit a number of devices per user)
6. Server will also keep the public key of this user (one public key per user device)

Download Publication
1. App will send a secret key to server via HTTPS, server will check if this key is valid.
2. If the key is valid, server will mark this session fully authorized to download publication.
3. Server then response with a password for publication zip file encrypted with user's public key.
4. Client, after received the response, send a file download request,
   server then response with file download response.
5. Client will use the password to extract publication zip file when a user open the publication.

* With this method, a hacker can use file system explorer program to copy cached publication file
  that was extract from zipped publication file. One possible way to prevent this is to use
  encrypted publication file instead of password-protected zip file.
  (http://aptogo.co.uk/2010/07/protecting-resources/)