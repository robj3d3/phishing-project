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