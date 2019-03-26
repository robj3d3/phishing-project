from flask import Blueprint

bp = Blueprint('auth', __name__) # Blueprint creation
# Blueprint named 'auth' created, with base folder (the blueprint's resource folder, i.e. ) __name__ (standard set argument)

from app.auth import routes # Registers auth.routes with the blueprint, at the bottom to avoid circular dependencies