============
FOSSEE Forum 
============

A **WebApp** to provide online discussion, question and answer for professional 
and programmers. 

Clone
-----

- Make sure your Internet is working.
- Clone this repo by typing ::

   git clone -b fossee-forum https://github.com/FOSSEE/spoken-tutorial-forums.git
   

Installation
------------

- Install Virtual Environment using the following command ::

    sudo apt-get install python-virtualenv

- Create a Virtual Environment ::

    virtualenv /path/to/virtualenv

- Activate the virtualenv using the command ::

    source /path/to/virtualenv-name/bin/activate

- Change the directory to the `spoken-tutorial-forums/` project using the command ::

    cd /path/to/spoken-tutorial-forums

- Install pre-requisites using the command ::

    pip install -r requirement.txt

  or you can also type ::

    easy_install `cat requirement.txt`


Usage
-----

- Using MySql (For development server only). Though, we recommend to use `mysql` for deployment
  server. See `settings.py` file for usage.

- Create 'forum' database in 'MySQL'.

- Only for Server deployment, Open `spoken-tutorial-forums/forums/settings.py` file and do the following changes ::

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


- For development on your machine, create a file `config.py` to `spoken-tutorial-forums/forums/` and write ::

    db_user='root' #(MySql username)
    
    db_pass = 'root' #(MySql password)
    
- For development on your machine, Open `spoken-tutorial-forums/forums/settings.py` file and do the following changes ::

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

	
- Populate the database using the following command ::

    cd /path/to/spoken-tutorial-forums
    
    python manage.py syncdb


- Run the script populate_category.py which enters lists of foss categories into the table category from the `category_names.txt` file ::
    
    python populate_category.py

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
