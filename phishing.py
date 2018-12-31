# this script calls the factory function create_app() as it is the only module in which
# the application now exists in the global scope (due to blueprints)
from app import create_app, db
from app.models import Staff, ScheduledEmails, Departments, Admin

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Staff': Staff, 'ScheduledEmails': ScheduledEmails, 'Departments': Departments, 'Admin': Admin}