from threading import Thread
from flask import render_template, current_app
from flask_mail import Message
from app import mail, db

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()

def send_phishing_email(staff, email):
    staff.delivered += 1 # maybe would be better to verify that email has been delivered
    db.session.commit()
    send_email('Account Under Attack!',
                sender=current_app.config['ADMINS'][0],
                recipients=[staff.email],
                text_body=render_template(('email/e_{}.txt').format(email),
                                            staff=staff),
                html_body=render_template(('email/e_{}.html').format(email),
                                            staff=staff))