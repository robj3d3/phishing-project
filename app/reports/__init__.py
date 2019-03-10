from flask import Blueprint

bp = Blueprint('reports', __name__) # Blueprint creation
# Blueprint named 'reports' created, with base folder (the blueprint's resource folder, i.e. ) __name__ (standard set argument)

from app.reports import routes # Registers reports.routes with the blueprint, at the bottom to avoid circular dependencies