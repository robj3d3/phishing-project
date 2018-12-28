import datetime, time, random
from phishing import app # app is the INSTANCE
from app import db # from app DIRECTORY
from app.models import Staff, ScheduledEmails

templates = ['office', 'dropbox', 'google']

def schedule_email(staff, days, templates):
    template = templates[random.randrange(len(templates) - 1)]
    send_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=random.randrange(24 * 60 * days))
    scheduled_email = ScheduledEmails(staff_email=staff.email, template=template, send_time=send_time, staff=staff)
    return scheduled_email

with app.app_context():
    while True:
        print("Looping")
        for staff in Staff.query.all():
            if (((datetime.datetime.utcnow() - staff.last_sent).days) >= 7) and (staff.direction == False) and (len(list(staff.scheduled_emails)) == 0):
                scheduled_email = schedule_email(staff, 3, templates)
                db.session.add(scheduled_email)
                print("Email scheduled 1", staff.email)
            elif (((datetime.datetime.utcnow() - staff.last_sent).days) >= 7) and (staff.risk_score >= 50) and (len(list(staff.scheduled_emails)) == 0):
                scheduled_email = schedule_email(staff, 3, templates)
                db.session.add(scheduled_email)
                print("Email scheduled 2", staff.email)
            elif ((datetime.datetime.utcnow() - staff.last_sent).days) >= 30 and (len(list(staff.scheduled_emails)) == 0):
                scheduled_email = schedule_email(staff, 3, templates)
                db.session.add(scheduled_email)
                print("Email scheduled 3", staff.email)
        db.session.commit()
        time.sleep(1800)

# (len(list(staff.scheduled_emails)) == 0) is to check there isn't already an email scheduled