from app import create_app, db
from app.models import Staff, ScheduledEmails, Departments, Admin

app = create_app() # Invokes the application factory create_app() function, returning an instance of the application

@app.shell_context_processor # This decorator registers a shell context processor function, i.e. when 'flask shell' is run in the CLI, it will invoke this function
                             # and register the items returned in the shell session.
def make_shell_context():
    return {'db': db, 'Staff': Staff, 'ScheduledEmails': ScheduledEmails, 'Departments': Departments, 'Admin': Admin} # Items to be registered in the shell session
    # Return must be a dictionary, with the keys representing the name the values will be referenced as in the CLI shell

