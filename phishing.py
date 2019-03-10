# In the CLI (command-line), the FLASK_APP environment variable is set to this module ("phishing.py"), which is used to specify how to load the application (upon calling 'flask run'),
# because it is in this module where the application instance is created.
# This script calls the factory function create_app() as it is the only module (excluding the emailer and scheduler) in which the application now exists in the
# global scope (due to blueprints).

from app import create_app, db
from app.models import Staff, ScheduledEmails, Departments, Admin

app = create_app() # Invokes the application factory create_app() function, returning an instance of the application

@app.shell_context_processor # This decorator registers a shell context processor function, i.e. when 'flask shell' is run in the CLI, it will invoke this function
                             # and register the items returned in the shell session.
def make_shell_context():
    return {'db': db, 'Staff': Staff, 'ScheduledEmails': ScheduledEmails, 'Departments': Departments, 'Admin': Admin} # Items to be registered in the shell session
    # Return must be a dictionary, with the keys representing the name the values will be referenced as in the CLI shell

# https://blog.miguelgrinberg.com/post/migrating-from-flask-script-to-the-new-flask-cli

# The shell starts a Python interpreter in the context of the application (i.e. it imports the application instance along with any imports specified in the shell 
# context (make_shell_context() function), meaning it can be used to directly access and modify the contents of the application database, as well as making testing
# specific back-end features of the application far easier.