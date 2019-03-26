import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os # This module provides a way of using operating system dependent functionality, e.g. for acccesing environment variables.
from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from config import Config
from flask_mail import Mail

db = SQLAlchemy() # Instantiates Flask-SQLAlchemy extension
migrate = Migrate() # Instantiates Flask-Migrate extension
mail = Mail() # Instantiates Flask-Mail extension
login = LoginManager() # Instantiates Flask-Login extension
login.login_view = 'auth.login' # Specifies log in view as auth.login such that any attempts to access a login_required view unauthorised are redirected to this view page
login.login_message = 'Administrator login required.' # Replaces default message which is flashed upon attempt to access a login_required view
bootstrap = Bootstrap() # Instantiates Flask-Bootstrap extension

def create_app(config_class=Config): # Application factory function constructs the application, passing the configuration class as the only argument.
    app = Flask(__name__) # Creates application object as instance of Flask class imported from the flask package. The __name__ variable passed is a predefined Python
                          # variable that tells the application where to look for templates, static files, etc. This will be equal to 'app' in this case as that is
                          # the name of the module in which it is used.
    app.config.from_object(config_class) # Loads the application's configuration using the Config object's values imported from the config.py file.

    db.init_app(app) # Instantiates Flask-SQLAlchemy extension for application instance (which is passed as the only argument)
    migrate.init_app(app, db) # Instantiates Flask-Migrate extension for application instance (which is passed as an argument as well as the Flask-SQLAlchemy database instance)
    mail.init_app(app)
    login.init_app(app)
    bootstrap.init_app(app)

    from app.auth import bp as auth_bp # Imports blueprint object from app.auth, imported directly above register_blueprint() call to avoid circular dependencies
    app.register_blueprint(auth_bp) # Registers auth_bp blueprint in application instance
    
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.reports import bp as reports_bp
    app.register_blueprint(reports_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    # When a blueprint is registered, any view functions, static files, templates, error handlers, etc. are connected to the application.

    if not app.debug and not app.testing: # only when FLASK_DEBUG=0 and it is not a unit test
        if app.config['MAIL_SERVER']: # True if ['MAIL_SERVER'] config variable is set. This means error emails will only be sent if the email server is configured.
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']: # Initialises optional credentials if they are set in the application's config.
                auth = (app.config['MAIL_USERNAME'],
                        app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']: # If TLS security protocol is set up, sets secure as an empty tuple, used only when authentication credentials are supplied.
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='Phishing-Project Failure',
                credentials=auth, secure=secure) # Returns a new instance of the SMTPHandler class, initialised using variables from the application's config dictionary.
            mail_handler.setLevel(logging.ERROR) # Only reports errors and not warnings/informational/debugging messages.
            app.logger.addHandler(mail_handler) # Flask uses Python's logging package, so already has a logger object to which the handler can be added.

        if not os.path.exists('logs'): # If a /logs directory doesn't exist, one will be created.
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/phishing-project.log',
                                           maxBytes=10240, backupCount=10) # Returns a new instance of the RotatingFileHandler class.
                                           # The first argument is the filename, maxBytes specifies the maximum size for each log file before it is 'rolled over'
                                           # and a new file created (10KB in this case), backupCount=10 specifies that only the last 10 log files are kept as backup.
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]')) # Sets a new instance of the Formatter class, formatting the log files to include the timestamp, logging level, message,
                                             # source file and line number from where the log entry originated.
        file_handler.setLevel(logging.INFO) # Sets threshold for file logger handler to INFO, which is one above the least severe (DEBUG). This makes the logs more comprehensive.
        app.logger.addHandler(file_handler) # Adds the handler to the application's logger object.

        app.logger.setLevel(logging.INFO) # Sets threshold for application logger handler to INFO.
        app.logger.info('Phishing-Project startup') # Writes line to signify startup, on a production server this will be used to signify a restart.

    return app # Returns application instance

from app import models # Database models imported at the bottom of the file to avoid circular dependencies.