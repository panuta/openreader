Deploy OpenReader on Amazon AWS
==========================================

Carefully follow these steps

Step 1 - Setup Amazon AWS account
------------------------------------------

- Setup EC2 instance from image __ami-c0c98c92__ (Ubuntu 10.04 64bit)

Step 2 - Fix locale problem
------------------------------------------

    $ sudo vim /etc/default/locale

Then set the following setting to the file

    LC_ALL="en_US.UTF-8"

Then

    $ export LC_ALL="en_US.UTF-8"

Step 3 - Config aptitude
------------------------------------------

    $ sudo vim /etc/apt/sources.list

Add the following at the end of file

    deb http://ap-southeast-1.ec2.archive.ubuntu.com/ubuntu/ lucid multiverse
    deb-src http://ap-southeast-1.ec2.archive.ubuntu.com/ubuntu/ lucid multiverse
    deb http://ap-southeast-1.ec2.archive.ubuntu.com/ubuntu/ lucid-updates multiverse
    deb-src http://ap-southeast-1.ec2.archive.ubuntu.com/ubuntu/ lucid-updates multiverse

Note: multiverse is for Amazon EC2 API Tools package

Then

    $ sudo apt-get update
    $ sudo apt-get upgrade

Step 4 - Install necessary packages
------------------------------------------

1. Install basic packages

    ```
    $ sudo apt-get install build-essential python2.6-dev python-setuptools libjpeg-dev zlib1g-dev libxml2-dev libpcre3-dev git-core
    ```

    Note:
    * libjpeg-dev and zlib1g-dev is for Python Imaging Library
    * libxml2-dev is for uWSGI
    * libpcre3-dev is for nginx

2. Install Django from https://www.djangoproject.com/download/

    ```
    $ sudo python setup.py install
    ````

3. Install django libraries

    ```
    https://github.com/ericflo/django-pagination
    https://github.com/django-debug-toolbar/django-debug-toolbar
    ```

4. Install PIL from http://www.pythonware.com/products/pil/

    ```
    $ sudo python setup.py build
    $ sudo python setup.py install --optimize=1
    ```

5. Install MuPDF from http://www.mupdf.com/

Step 5 - Install EC2 API Tools
------------------------------------------

1. Create X.509 certificate and private key

    1. Go to https://aws-portal.amazon.com/gp/aws/securityCredentials
    2. Under __Access Credentials__ select tab __X.509 Certificates__
    3. Create a new certificate and download file

2. Copy file __px-xxxxxx.pem__ and __cert-xxxxxx.pem__ to EC2 server

3. Install package

    ```
    $ sudo apt-get install ec2-api-tools
    ```

    Note: Don't forget to add multiverse to sources.list before install this package

4. Add the following line to $HOME/.bashrc

    ```
    export EC2_KEYPAIR=<your keypair name> # name only, not the file name
    export EC2_URL=https://ec2.<your ec2 region>.amazonaws.com
    export EC2_PRIVATE_KEY=$HOME/<where your private key is>/pk-XXXXXXXXXXXXXXXXXXXXXXXXXXXX.pem
    export EC2_CERT=$HOME/<where your certificate is>/cert-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.pem
    export JAVA_HOME=/usr/lib/jvm/java-6-openjdk/
    ```
    
    Note:
    * __your keypair name__ is your keypair name in https://console.aws.amazon.com/ec2/home?region=ap-southeast-1#s=KeyPairs
    * __your ec2 region__ in this case is __ap-southeast-1__
    * __EC2_PRIVATE_KEY__ and __EC2_CERT__ is a location of private key and certificate that you have downloaded from AWS console and uploaded to this EC2 instance

Step 5 - Setup project folders
------------------------------------------

```
$ sudo mkdir /web
$ cd /web
$ sudo mkdir openreader
$ cd openreader
$ sudo mkdir source www run conf bin logs
```

Step 6 - Setup git and download source code from GitHub
------------------------------------------

1. Create a key for GitHub

    ```
    $ sudo ssh-keygen -t rsa -C "openreader@ec2"
    ```

2. Add content of __$HOME/.ssh/id_rsa.pub__ to GitHub website (https://github.com/panuta/openreader/admin/keys)

3. Clone OpenReader source code from GitHub

    ```
    $ cd /web/openreader/source
    $ sudo git clone git@github.com:panuta/openreader.git
    ```

Step 8 - Setup Postgresql database
------------------------------------------

1. Install Postgresql (Postgresql version for Ubuntu 10.04 is 8.4)

    ```
    $ sudo apt-get install postgresql python-psycopg2
    ```

2. Change 'postgres' user password

    ```
    $ sudo -u postgres psql postgres
    postgres=# \password postgres
    ```

3. Create database

    ```
    $ sudo -u postgres createdb openreader
    $ sudo -u postgres createuser -SDRP openreader
    ```

4. Config pg_hba.conf file

    ```
    $ cd /etc/postgresql/8.4/main
    $ sudo vim pg_hba.conf
    ```

    Then add this line

    ```
    local openreader openreader  md5
    ```

    Reload Postgresql server

    ```
    $ sudo -u postgres /etc/init.d/postgresql-8.4 reload
    ```

Step 9 - Setup web server
------------------------------------------

1. Download nginx and uWSGI

    - nginx http://nginx.org/en/download.html
    - uWSGI http://projects.unbit.it/uwsgi/wiki/WikiStart#Getit

2. Extract uWSGI and build

    ```
    $ sudo python uwsgiconfig.py --build
    ```
    
    Then copy uWSGI binary file to project folder
    
    ```
    $ sudo cp uwsgi /web/openreader/bin/
    ```

3. Extract and install nginx

    ```
    $ sudo ./configure --conf-path=/web/openreader/conf/nginx/nginx.conf
    $ sudo make
    $ sudo make install
    ```

4. Enable port 80 access for EC2 instance

    ```
    $ ec2-authorize default -p 80
    ```

Step 10 - Run server
------------------------------------------

1. Copy or replace server configuration files from OpenReader source __misc__ folder

    ```
    $ sudo cp /web/openreader/source/openreader/misc/server/uwsgi_openreader.ini /web/openreader/conf/
    $ sudo cp /web/openreader/source/openreader/misc/server/nginx.conf /web/openreader/conf/nginx/
    ```

2. Create an Elastic IP and attached to this EC2 instance (https://console.aws.amazon.com/ec2/home?region=ap-southeast-1&#s=Addresses)

3. Create openreader init script

    1. Copy openreader from OpenReader source __misc__ folder to __/etc/init.d/__
    2. Execute

    ```
    TODO
    ```

4. Edit django settings file

    TODO

5. Set folder permission

    TODO

Resources
==========================================

https://help.ubuntu.com/community/EC2StartersGuide