import os # This module provides a way of using operating system dependent functionality, e.g. for acccesing environment variables - https://docs.python.org/3/library/os.html
from dotenv import load_dotenv # This module facilitates using .env file to store manually set environment variables, useful for managing settings in development and production - https://github.com/theskumar/python-dotenv
from datetime import timedelta

# This application depends on a lot of environment variables, and so it is common practice for these variables to be stored in a .env file in the root application directory.

basedir = os.path.abspath(os.path.dirname(__file__)) # Returns normalised absolutised version of the application's main directory pathname.
load_dotenv(os.path.join(basedir, '.env')) # Loads a .env file, which contains any manually set environment variables.
# These lines come before the definition of the Config class, such that the environment variables in the .env file are used (as they need to be imported first).
# FLASK_APP and FLASK_DEBUG environment variables cannot be set in the .env file as they are needed early in the application bootstrap process, prior to application instantiation.

# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xv-a-better-application-structure

class Config(object):
    # os.environ.get() returns the enviroment variable at the pathname passed as the argument. It is good practice to use this to set configuration variables instead
    # of using hardcoded strings, because when the application is deployed on a production server, it can use the production server's variables. This improves ease
    # of integration into the production server's sytem.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess' # http://flask.pocoo.org/docs/1.0/quickstart/
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db') # Sets database URI that should be used for the connection, if no environment variable is defined, a database
                                                       # named 'app.db' is configured, located in the main directory of the application (which is stored in the basedir variable)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER') # Sets config variable for email server as environment variable
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25) # Sets config variable for email server port as environment variable, but uses standard port 25 (SMTP) if not set 
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None # Boolean value, config variable is True if encrypted connections are enabled
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') # Sets email server credentials if necessary
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['robmailserver@gmail.com'] # List of email addresses that will receive error reports
    POSTS_PER_PAGE = 5 # Number of items (staff member records) displayed per paginated page
    SERVER_NAME = 'local.docker:5000' # Specifies server name on which the application runs, will be set to production server's domain on deployment
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=5) # Session timeout time

# On one hand, setting SERVER_NAME = 127.0.0.1 allows link creation for emailer, but invalidates forms (CSRF invalidation)
# However, localhost:5000 fixes invalidation and URL generation but flask app is running on 127.0.0.1 so won't load on localhost:5000
# "The spec for rejecting cookies states that domain names must be a fully qualified domain name with a TLD (.com, etc.) or be an exact IP address."
# setting etc\hosts file for 127.0.0.1 to local.docker compromises, specifying a server name allows for URL generation and a FQDN means CSRF tokens validate

# Flask-WTF forms make use of the SECRET_KEY to protect web forms against CSRF attacks. It uses the key to generate tokens and signatures.
# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms


# https://docs.python.org/3/library/os.html#os.environ

# https://docs.python.org/2/library/os.path.html

# http://flask-sqlalchemy.pocoo.org/2.3/config/