from flask import render_template
from app import db
from app.errors import bp

@bp.app_errorhandler(400) # Registers an error handler function to handle error status code HTTP 400 (Bad Request)
def bad_request_error(error):
    return render_template('errors/400.html'), 400 # Handler returns contents of respective template, second value returned is the error status code (400)

@bp.app_errorhandler(404) # Registers an error handler function to handle error status code HTTP 404 (Not Found)
def not_found_error(error):
    return render_template('errors/404.html'), 404   

@bp.app_errorhandler(500) # Registers an error handler function to handle error status code HTTP 500 (Internal Server Error)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500


# http://flask.pocoo.org/docs/1.0/api/

# app_errorhandler() is like Flask.errorhandler() but for a blueprint. It registers an error handler for all requests, even if outside of the blueprint. This means
# that I only have to register the error handlers in this file, and they apply for all respective error requests across the application.

# The purpose of using error handlers is to keep the user interface consistent across the application. The error handlers I have initialised return a render_template()
# with the template being a custom error page that includes a 'Back' hyperlink, which the system administrator can click to return to the index page.