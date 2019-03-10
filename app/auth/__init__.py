from flask import Blueprint

bp = Blueprint('auth', __name__) # Blueprint creation
# Blueprint named 'auth' created, with base folder (the blueprint's resource folder, i.e. ) __name__ (standard set argument)

from app.auth import routes # Registers auth.routes with the blueprint, at the bottom to avoid circular dependencies

# http://flask.pocoo.org/docs/1.0/blueprints/
# The main purpose of using blueprints (as explained in the Documented Design section) is to improve code reusability, but also to better readability

# http://flask.pocoo.org/docs/1.0/tutorial/templates/
# The folder in which Flask template files are stored is called 'templates'. However, blueprints facilitate the specification (as an optional argument in the constructor)
# of a template folder which is added to the search path of templates with a lower priority than the actual application's template folder. This provides the ability
# to, for example, have two templates called 'index.html'; one for the main application and another for a blueprinted subsection of the application, such as /reports,
# without the former overriding the latter. It also facilitates the file structuring such that you can store templates in a folder within the blueprint's resource folder hierarchy, e.g. /app/auth/templates
# However, for this application I would prefer, for sake of readability, to have my templates under a single hierarchy. Therefore there is no need to specify this argument
# as I am using the Flask default app/templates folder.