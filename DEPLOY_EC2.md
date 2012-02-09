Deploy OpenReader on Amazon AWS
==========================================

Carefully follow these steps

Step 1 - Setup Amazon AWS account
------------------------------------------

- Setup EC2 instance from "ami-c0c98c92" (Ubuntu 10.04 64bit)

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

Then

    $ sudo apt-get update
    $ sudo apt-get upgrade

Step 4 - Install necessary packages
------------------------------------------

1. Install basic packages

```
$ sudo apt-get install build-essential python2.6-dev libjpeg-dev zlib1g-dev libxml2-dev libpcre3-dev
```

Note: libjpeg-dev and zlib1g-dev is for PIL, libxml2-dev is for uwsgi, libpcre3-dev is for nginx http rewrite module

2. Install Django from https://www.djangoproject.com/download/

3. Install python libraries

```
$ sudo apt-get install python-setuptools
```

4. Install django libraries

```
https://github.com/ericflo/django-pagination
https://github.com/django-debug-toolbar/django-debug-toolbar
```

5. Install PIL (http://www.pythonware.com/products/pil/)

```
$ sudo python setup.py build
$ sudo python setup.py install --optimize=1
```

Step 5 - Install EC2 API Tools
------------------------------------------

1. Create x.509 and private key from https://aws-portal.amazon.com/gp/aws/securityCredentials X.509 Certificates tab

2. Copy file px-xxx.pem and cert-xxx.pem to EC2 server

3. Install package

```
$ sudo apt-get install ec2-api-tools
```

4. Add the following line to $HOME/.bashrc

```
export EC2_KEYPAIR=<your keypair name> # name only, not the file name
export EC2_URL=https://ec2.<your ec2 region>.amazonaws.com
export EC2_PRIVATE_KEY=$HOME/<where your private key is>/pk-XXXXXXXXXXXXXXXXXXXXXXXXXXXX.pem
export EC2_CERT=$HOME/<where your certificate is>/cert-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.pem
export JAVA_HOME=/usr/lib/jvm/java-6-openjdk/
```

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

1. Install Git

```
$ sudo apt-get install git-core
```

2. Setup key

```
$ ssh-keygen -t rsa -C "openreader@ec2"
```

3. Add content of id_rsa.pub to GitHub website (https://github.com/panuta/openreader/admin/keys)

4. In case you created the key using other username, copy folder .ssh to /root

```
$ sudo cp -R ~/.ssh /root
```

5. Download source code from GitHub

```
$ cd /web/openreader/source
$ sudo git clone git@github.com:panuta/openreader.git
```

Step 8 - Setup Postgresql database
------------------------------------------

1. Install Postgresql

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

Add this line

```
local openreader openreader  md5
```

Then

```
$ sudo -u postgres /etc/init.d/postgresql-8.4 reload
```

Step 9 - Setup web server
------------------------------------------

1. Download nginx and uWSGI

```
http://nginx.org/en/download.html
http://projects.unbit.it/uwsgi/wiki/WikiStart#Getit
```

2. Build uWSGI

```
$ sudo python uwsgiconfig.py --build
$ sudo cp uwsgi /web/openreader/bin/
```

3. Install nginx

```
$ sudo ./configure --conf-path=/web/openreader/conf/nginx/nginx.conf
$ sudo make
$ sudo make install
```

4. Enable port 80 access

```
$ ec2-authorize default -p 80
```

Step 10 - Run server
------------------------------------------

1. Copy uWSGI ini file to /web/openreader/conf/

2. Copy nginx conf file to /web/openreader/conf/nginx/

3. 

Resources
==========================================

https://help.ubuntu.com/community/EC2StartersGuide