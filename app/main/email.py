from threading import Thread
from flask import render_template, current_app
from flask_mail import Message
from app import mail, db
import datetime

def send_async_email(app, msg): # Flask uses contexts to avoid having to pass arguments across functions (in this case, config stored needs to be accessed).
    with app.app_context():  # The application context created using 'with app.app_context()' makes the application instance accessible via the current_app Flask variable.
        mail.send(msg) # Verifies and sends message (email)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients) # Encapsulates an email message, setting email subject, sender address and recipient addresses from passed parameters.
    msg.body = text_body # Sets email's plain text message
    msg.html = html_body # Sets email's HTML message - setting both plain text and HTML email bodies ensures the email will be readable however it is accessed (i.e. browser vs in-app).
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()

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

