


Celery on OSX for Development
==========

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