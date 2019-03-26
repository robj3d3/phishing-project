import os # This module provides a way of using operating system dependent functionality, e.g. for acccesing environment variables
from dotenv import load_dotenv # This module facilitates using .env file to store manually set environment variables, useful for managing settings in development and production
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__)) # Returns normalised absolutised version of the application's main directory pathname.
load_dotenv(os.path.join(basedir, '.env')) # Loads a .env file, which contains any manually set environment variables.

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess' # Flask-WTF forms make use of the SECRET_KEY to protect web forms against CSRF attacks. It uses the key to generate tokens and signatures.
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