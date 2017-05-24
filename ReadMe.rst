============
FOSSEE Forum 
============

Documentation for installation of requirements for FOSSEE-forum project

Clone
-----

- Make sure your Internet is working.
- Clone this repo by typing ::

   git clone https://github.com/FOSSEE/FOSSEE-Forum.git


Installation
------------

- Install Virtual Environment. Virtual environment is used to make the installation easier, and will help to avoid clutter in the system
  wide libraries. Use the following command ::

    sudo apt-get install python-virtualenv

- Create a Virtual Environment ::

    virtualenv /path/to/virtualenv-name

- Activate the virtualenv using the command ::

    source /path/to/virtualenv-name/bin/activate

- Change the directory to the `FOSSEE-forum/` project using the command ::

    cd /path/to/FOSSEE-forum

- Install pre-requisites using the command (please don't use sudo) ::

    pip install -r requirements.txt

-Install MySQL using the following command ::

    sudo apt-get install mysql-server


Usage
-----

- Using MySQL (For development server only). Though, we recommend to use `MySQL` for deployment
  server. See `settings.py` file for usage.

- Create 'forum' database in 'MySQL'.
  Open 'MySQL' using the following command ::

	mysql -u root -p

  and then create database using following command ::

	create database forum

- Only for Server deployment, open `spoken-tutorial-forums/forums/settings.py` file and make the following changes ::

    DATABASES = {
        'default': {
        'ENGINE': 'django.db.backend.mysql',
        'NAME'  : 'forum', 
        'USER': '', 
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        }
    }


- For development on your machine, create a file `config.py` in `spoken-tutorial-forums/forums/` and add ::

    db_user='root' #(MySql username)

    db_pass = 'root' #(MySql password)

  Then open file FOSSEE_forums/forums/layout.py and change following to yours ::

    DB_USER
    DB_PASS
    TO_EMAIL_ID



- For development on your machine, open `FOSSEE-forums/forums/settings.py` file and make the following changes ::

    DATABASES = {
        'default': {
        'ENGINE': 'django.db.backend.mysql',
        'NAME'  : 'forum', 
        'USER': db_user, 
        'PASSWORD': db_pass ,
        'HOST': '',
        'PORT': '',
        }
    }


- Migrate the database using the following command ::

    cd /path/to/FOSSEE-forum

    python manage.py makemigrations

    python manage.py migrate

    python manage.py makemigrations website

    python manage.py migrate website


- Run the following command to populate the category in the database ::

    python manage.py populatecategory


- Start the server using the command ::

    python manage.py runserver



Contributing
------------

- Never edit the master and fossee-forum branch.
- Make a branch specific to the feature you wish to contribute on.
- Send me a pull request.
- Please follow `PEP8 <http://legacy.python.org/dev/peps/pep-0008/>`_
  style guide when coding in Python.

License
-------

GNU GPL Version 3, 29 June 2007.

Please refer this `link <http://www.gnu.org/licenses/gpl-3.0.txt>`_
for detailed description.
