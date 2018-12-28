import datetime
from phishing import app # app is the INSTANCE
from app import db # from app DIRECTORY
from app.models import Staff, ScheduledEmails
from app.main.email import send_phishing_email


import datetime

with app.app_context():
    while True:
        scheduled = ScheduledEmails.query.order_by(ScheduledEmails.send_time).limit(10).all() # returns first 10 records, ordered by send_time
        for e in scheduled:
            utcnow = datetime.datetime.utcnow() # checks time UTC now
            now_time = utcnow.year, utcnow.month, utcnow.day, utcnow.hour, utcnow.minute # converts to resolution of minutes
            send_time = e.send_time.year, e.send_time.month, e.send_time.day, e.send_time.hour, e.send_time.minute
            if send_time == now_time: # check to see if, given resolution of 1 minute, UTC now == send time of email
                if e.sent == False:
                    e.sent = True
                    db.session.commit()
                    print("Email sent", e.staff, e.staff_email, e.send_time)
                    send_phishing_email(e.staff, e.template)
                    db.session.delete(e) # delete scheduled email record to avoid data redundancy and to allow scheduler to continue
                    db.session.commit()
                else:
                    continue
            else:
                continue
