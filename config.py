import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['robmailserver@gmail.com']
    POSTS_PER_PAGE = 5
    SERVER_NAME = 'local.docker:5000'
# On one hand, setting SERVER_NAME = 127.0.0.1 allows link creation for emailer, but invalidates forms (CSRF invalidation)
# However, localhost:5000 fixes invalidation and URL generation but flask app is running on 127.0.0.1 so won't load on localhost:5000
# "The spec for rejecting cookies states that domain names must be a fully qualified domain name with a TLD (.com, etc.) or be an exact IP address."
# setting etc\hosts file for 127.0.0.1 to local.docker compromises, specifying a server name allows for URL generation and a FQDN means CSRF tokens validate