from flask import Blueprint

bp = Blueprint('main', __name__) # Blueprint creation
# Blueprint named 'main' created, with base folder (the blueprint's resource folder, i.e. ) __name__ (standard set argument)

from app.main import routes # Registers main.routes with the blueprint, at the bottom to avoid circular dependencies