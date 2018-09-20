============
FOSSEE Forum 
============

A **Website** to provide online discussion, question and answer for professionals
and programmers on niche areas.

Clone
-----

- Make sure your Internet is working.
- Clone this repo by typing ::

   git clone -b fossee-forum https://github.com/FOSSEE/FOSSEE-Forum.git
   

Installation
------------

- Install Virtual Environment using the following command ::

    sudo apt-get install python-virtualenv

- Create a Virtual Environment ::

    virtualenv /path/to/virtualenv

- Activate the virtualenv using the command ::

    source /path/to/virtualenv-name/bin/activate

- Change the directory to the ``spoken-tutorial-forums/`` project using the command ::

    cd /path/to/spoken-tutorial-forums

- Install pre-requisites using the command (please don't use sudo) ::

    pip install -r requirements.txt

  or you can also type ::

    easy_install `cat requirements.txt`


Usage
-----

- Using MySQL (For development server only). Though, we recommend to use ``MySQL`` for deployment
  server as well. See `settings.py` file for usage.

- Create 'forums' database in 'MySQL'.

- Only for Server deployment, open ``FOSSEE-Forum/forums/settings.py`` file and make the following changes ::

    DATABASES = {
        'default': {
        'ENGINE': 'django.db.backend.mysql',
        'NAME'  : 'forums', 
        'USER': '', 
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        }
    }


- For development on your machine, create a file ``local.py`` in ``FOSSEE-Forum/forums/`` and add ::

    DB_USER = 'root' # (MySql username)
    DB_PASS = 'root' # (MySql password)

    # To be obtained from FOSSEE-Forums admin
    PUB_KEY = ''
    PRIV_KEY = ''

    # To be obtained from https://www.google.com/recaptcha/admin#list
    FORUM_GOOGLE_RECAPTCHA_SECRET_KEY = ''
    FORUM_GOOGLE_RECAPTCHA_SITE_KEY = ''
    
- For development on your machine, open ``FOSSEE-Forum/forums/settings.py`` file and make the following changes ::

    DATABASES = {
        'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME'  : 'forums',
        'USER': DB_USER,
        'PASSWORD': DB_PASS,
        'HOST': '',
        'PORT': '',
        }
    }

- Set up the database ``forums`` by typing ``sudo mysql -u root -p`` in the terminal to log into MySQL ::

    mysql> CREATE DATABASE forums;
    mysql> GRANT ALL PRIVILEGES ON forums.* TO 'username'@'hostname' IDENTIFIED BY 'password'

- Get the database file from FOSSEE-Forum admin and dump data into ``forums`` databse ::

    sudo mysqldump -u [username] -p[password] forums < database.sql

- Comment line 10 and lines 34-48 in ``spamFilter.py`` as these will work only when Question and Answer model is present in database
	
- Populate the database using the following command ::

    cd /path/to/FOSSEE-Forum
    
    python manage.py makemigrations
    python manage.py migrate
    python manage.py makemigrations website
    python manage.py migrate website


- Run the script ``populate_category.py`` which enters lists of foss categories into the table category from the `category_names.txt` file ::
    
    python populate_category.py

- Start the server using the command ::

    python manage.py runserver

- You can add a superuser and a user for the forum using the command ::

    python manage.py createsuperuser

- Modify the webapp using Django admin panel and login to explore all the features of the website


**Not for first time users and only for developers**
Migration
----------
(How to add a new model field to an existing database)

- Enter into virual environment

- Change the directory to the ``FOSSEE-Forum/`` project using the command ::

    cd /path/to/FOSSEE-Forum

- Run below command to create required migration commands ::

    python manage.py makemigrations

- Execute the required migrations ::
   
    python manage.py migrate

- Make the change to the website model, for example, you can add a model ::
    
    class TestModel(models.Model):
        name = models.CharField(max_length=100)

- Create a migration for your new change ::

    python manage.py makemigrations website

- Apply new migration ::

    python manage.py migrate website

    


Contributing
------------

- Fork the repository to contribute changes.
- It is preferable to make a branch specific to the feature you wish to contribute on.
- Send a pull request.
- Please follow `PEP8 <http://legacy.python.org/dev/peps/pep-0008/>`_
  style guide when coding in Python.

License
-------

GNU GPL Version 3, 29 June 2007.

Please refer this `link <http://www.gnu.org/licenses/gpl-3.0.txt>`_
for detailed description.
