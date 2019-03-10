from flask import Blueprint

bp = Blueprint('errors', __name__) # Blueprint creation
# Blueprint named 'errors' created, with base folder (the blueprint's resource folder, i.e. ) __name__ (standard set argument)

from app.errors import handlers # Registers errors.handlers with the blueprint, at the bottom to avoid circular dependencies