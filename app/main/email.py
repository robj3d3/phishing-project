from threading import Thread
from flask import render_template, current_app
from flask_mail import Message
from app import mail, db
import datetime

def send_async_email(app, msg): # Flask uses contexts to avoid having to pass arguments across functions (in this case, config stored needs to be accessed).
    with app.app_context():  # The application context created using 'with app.app_context()' makes the application instance accessible via the current_app Flask variable.
        mail.send(msg) # Verifies and sends message (email)

# http://flask.pocoo.org/docs/1.0/appcontext/

# As stated in Flask's documentation, a Flask application object has attributes, such as config, that are useful to access within views and CLI (command-line) commands.
# However, importing the app instance within modules is prone to circular import issues/dependencies. As a fix, Flask uses application contexts. Instead of referring
# to the app instance directly, you can use the current_app proxy, which points to the application handling the current activity.
# Application context is required to send the email in the send_async_email() function, as the mail.send() method needs to access the configuration values for the
# email server, which can only be done by knowing what the application is.

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients) # Encapsulates an email message, setting email subject, sender address and recipient addresses from passed parameters.
    msg.body = text_body # Sets email's plain text message
    msg.html = html_body # Sets email's HTML message - setting both plain text and HTML email bodies ensures the email will be readable however it is accessed (i.e. browser vs in-app).
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()
           # Using current_app directly in the send_async_email() function that runs as the background thread does not work, as threads are designed to be scheduled to execute
           # in the background when the processor is free, and as such in a different thread the current_app would have no value assigned (as it is a context-aware variable).
           # By a 'context-aware' variable, it means current_app is a proxy object which points to the application handling the current activity. Thus, passing
           # current_app as an argument when Thread() is invoked wouldn't work for the same reason. Instead, the real application instance needs to be extracted
           # from the proxy object. This is achieved using current_app._get_current_object().
           # Otherwise you get RuntimeError: Working outside of application context.

           # https://www.reddit.com/r/flask/comments/5jrrsu/af_appapp_context_in_thread_throws_working/
           # http://flask.pocoo.org/docs/1.0/reqcontext/ - proxy object
           # https://pythonhosted.org/Flask-Mail/

# https://docs.python.org/2/library/threading.html
# https://pythonhosted.org/Flask-Mail/

# Thread() constructor arguments: target is the callable object to be invoked by the run() method, args is the argument tuple passed into the target object.
# .start() at the end of the Thread() call is to start the thread's activity, which arranges for the object's run() method to be invoked in a separate thread
# of control.

def send_phishing_email(staff, template): # Function invoked in the view functions/by the emailer script to send a test phishing email
    if staff.delivered == 0: # Direction of progress logic flaw solution... (0 risk score) and (emails delivered > 0) = decreasing risk, opposed to default increasing risk
        staff.direction = True
    staff.delivered += 1 # Increments staff's delivered attribute by 1
    staff.last_sent = datetime.datetime.utcnow() # Sets staff member's last_sent attribute to the datetime at which the email is sent (hence this is always the datetime of the last email sent to this staff member)
    db.session.commit() # Commits database object changes to the database.
    send_email('Account Under Attack!',
                sender=current_app.config['ADMINS'][0],
                recipients=[staff.email],
                text_body=render_template(('email/e_{}.txt').format(template),
                                            staff=staff),
                html_body=render_template(('email/e_{}.html').format(template),
                                            staff=staff)) # Invokes send_email() function, passing arguments including email subject, sender address (which is the
                                                          # first email address in the list of admin addresses from config), recipient address (the staff member's
                                                          # email), and email plain text and HTML bodies.

# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-x-email-support

# The processes that occur when sending an email slow down the application considerably, and therefore I needed a method of making the sending of emails asychronous.
# i.e., when the send_email() function is called, the task of sending the email is scheduled to happen in the background, freeing the send_email() function and
# improving the speed of the application. This process is known as threading. A thread is a basic unit to which the operating system allocates processer time.

# In summary, when the send_phishing_email() function is called, it calls the send_email() function which creates a background thread of the send_async_email()
# function, passing the arguments current_app._get_current_object() and msg. The send_async_email() function then calls the mail.send() function with application
# context, which uses the Mail instance configured with the application to send the email.