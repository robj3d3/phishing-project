from threading import Thread
from flask import render_template, current_app
from flask_mail import Message
from app import mail

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()

def send_phishing_email(staff):
    send_email('Account Under Attack!',
                sender=current_app.config['ADMINS'][0],
                recipients=[staff.email],
                text_body=render_template('email/email1.txt',
                                            staff=staff),
                html_body=render_template('email/email1.html',
                                            staff=staff))