import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os # This module provides a way of using operating system dependent functionality, e.g. for acccesing environment variables - https://docs.python.org/3/library/os.html
from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from config import Config
from flask_mail import Mail

# When using blueprints to make a modular application, one common pattern is to create the application object when the blueprints are imported. However, if instead
# the application object creation is moved into a function that can be separately invoked, multiple instances of the same application can be created.
# One of the main advantages of this is that it makes testing easier, more flexible and more reliable, as you can test multiple different application configurations
# by creating a different application instance for each configuration. If tests used the same application for each configuration, one test could make changes to
# the application that affects another test that runs later. This is poor practice and can lead to a variety of obscure bugs. Being able to make multiple
# application instances is also handy in a number of other circumstances.

db = SQLAlchemy() # Instantiates Flask-SQLAlchemy extension
migrate = Migrate() # Instantiates Flask-Migrate extension
mail = Mail() # Instantiates Flask-Mail extension
login = LoginManager() # Instantiates Flask-Login extension
login.login_view = 'auth.login' # Specifies log in view as auth.login such that any attempts to access a login_required view unauthorised are redirected to this view page
login.login_message = 'Administrator login required.' # Replaces default message which is flashed upon attempt to access a login_required view
bootstrap = Bootstrap() # Instantiates Flask-Bootstrap extension

# https://flask-login.readthedocs.io/en/latest/

# When the application does not exist as a global variable, the method of initialising Flask extensions is to first create the extension instance in the global
# scope, without passing any arguments to it. This creates an instance of the extension that is not initially bound to the application. Upon instantiation of
# the application, the init_app() method is invoked to bind the extension instance to the application. Using this design pattern, no application-specific state
# is stored on the extension objects, so one extension object can be used for multiple application instances.

def create_app(config_class=Config): # Application factory function constructs the application, passing the configuration class as the only argument.
    app = Flask(__name__) # Creates application object as instance of Flask class imported from the flask package. The __name__ variable passed is a predefined Python
                          # variable that tells the application where to look for templates, static files, etc. This will be equal to 'app' in this case as that is
                          # the name of the module in which it is used.
    app.config.from_object(config_class) # Loads the application's configuration using the Config object's values imported from the config.py file.

    # https://stackoverflow.com/questions/15122312/how-to-import-from-config-file-in-flask
    # http://flask.pocoo.org/docs/1.0/config/

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
                credentials=auth, secure=secure) # Returns a new instance of the SMTPHandler class, initialised using variables from the application's confg dictionary.
            mail_handler.setLevel(logging.ERROR) # Only reports errors and not warnings/informational/debugging messages.
            app.logger.addHandler(mail_handler) # Flask uses Python's logging package, so already has a logger object to which the handler can be added.

            # https://docs.python.org/3.6/library/logging.handlers.html#smtphandler

        # When the application is deployed on a production server, the CLI (command-line) output is not going to be regularly monitored, and so there needs to be
        # a way of alerting the system administrator to any errors that occur such that they can be fixed as quickly as possible. One approach is to configure Flask
        # to send an email to the system administrator immediately upon the occurence of the error.
    

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

        # https://docs.python.org/3.6/library/logging.handlers.html#rotatingfilehandler
        # https://docs.python.org/2/library/logging.html
        # https://docs.python.org/3.6/howto/logging-cookbook.html

        # Some failure conditions do not end in Python exceptions, and being able to log the development of the application can be very useful for debugging.
        # Therefore, maintaining a log file for the application will be very useful.

    return app # Returns application instance

    # https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-vii-error-handling

from app import models # Database models imported at the bottom of the file to avoid circular dependencies.

# http://flask.pocoo.org/docs/1.0/patterns/appfactories/
# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xv-a-better-application-structure