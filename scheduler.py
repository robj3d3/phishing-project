import datetime, time
from phishing import app # app is the INSTANCE
from app import db # from app DIRECTORY
from app.models import Staff, ScheduledEmails

with app.app_context():
    # staff = Staff.query.all()
    # d = datetime.datetime(2018, 8, 1, 17, 30, 0, 0)
    # for s in staff:
    #     email = ScheduledEmails(staff_email=s.email, template='office', send_time=d, staff=s)
    #     db.session.add(email)
    #     db.session.commit()
    emails = ScheduledEmails.query.all()
    print(emails)
    for e in emails:
        print(e.id, e.staff_id, e.staff_email, e.template, e.send_time, e.sent)
#    while True:
#        staff = Staff.query.all()
#
#        for s in staff:
#            print(s.staff_name)
#
#        time.sleep(3)


# import datetime
# staff = Staff.query.get(1)
# scheduled_email = ScheduledEmails(staff_email=staff.email, template='office', send_time=datetime.datetime(2018, 8, 1, 16, 55, 0, 0), staff=staff) # last bit is the backref