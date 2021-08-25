# Rallye-Server

The rallye server is a [django](https://www.djangoproject.com) tool for rating the performance of groups participating in the campus rallye. The campus rallye is part of the program of the [Study Introduction Days](https://mpi.fs.tum.de/en/entering-tum/set/) of the Mathematics/Phyics/Informatics Departmental Student Council at Technical University Munich. <br>

The campus rallye consists of stations, which are supervised by tutors.
Participating students form groups of four to six people. Each group absolves different stations where they can get at max 10 points per stations. The tutors log in to the rallye server and fill in the ratings of the groups.
Additionally the tutors have the possiblity to update the ratings if they filled in the wrong number of points of to delete the rating if they rated the wrong group in the tool. <br>
At the end of the campus rallye, a prize giving ceremony follows. This ceremony is supported by the automatic evalutation of the total ratings ot the groups.

## Getting Started
### Prerequisites
You need to have [Python 3](https://www.python.org) and [PyPI](https://pypi.org) installed. <br>
Furthermore you should set up a [virtual environment](https://virtualenv.pypa.io/en/stable/). <br>
And you need to have [Postgres](https://www.postgresql.org) installed.

### Installing
This guides assumes you use MacOS (most of it should also work for other Linux Distributions). <br>
#### Set up Python
```python
# Install python 3 and pip3
brew install python3
# Install virtual environment
pip3 install virtualenv
# Create virtual environment
virtualenv <nameofvirtenv>
# Activate the virtualenv
source <nameofvirtenv>/bin/activate
# Install the required software (listed in requirements.txt)
pip install -r requirements.txt
```
Now that the python part is set up we need to take care of the database. <br>
#### Set up Database
I suggest you install the [Postgres.app](https://postgresapp.com) which is a graphical postgres application. <br>
After installing you just double click on the "postgres" database. This opens the commandline:
```python
# Set a password for the postgres user
\password postgres;
# Create the database you want to use for the tool
CREATE DATABASE ratingsdb;
# Create a user
CREATE USER djangodbuser WITH PASSWORD 'djangodbuserpwd';
ALTER ROLE djangodbuser SET client_encoding TO 'utf8';
ALTER ROLE djangodbuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE djangodbuser SET timezone TO 'UTC';
# Grant the user access to the database
GRANT ALL PRIVILEGES ON DATABASE <dbname> TO djangodbuser;
# Exit Postgres
\q
```

#### Set Local Settings
To define the production settings of the django application we define the file `local_settings.py` under `serverproject/server`.
A template for the file:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '<production-db-name>',
        'USER': '<production-db-user>',
        'PASSWORD': '<production-db-password>',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

SECRET_KEY = '<SECRET_KEY>'
ALLOWED_HOSTS = ['<FQDN>']
DEBUG = False
```

#### Start the project
```python
# Navigate to project and start the server
python manage.py runserver
# Open the url http://127.0.0.1:8000/
# Lateron deactivate the virtual environment
deactivate
```

### Deployment
For deployment in production I recommend [this tutorial from DigitalOcean](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-16-04).

## Authors
[Florian Angermeir](angermeir.me)

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
