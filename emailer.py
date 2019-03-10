import datetime
from phishing import app # app is the INSTANCE
from app import db # from app DIRECTORY
from app.models import Staff, ScheduledEmails
from app.main.email import send_phishing_email

import datetime

with app.app_context(): # Requires application context to access the database and query the ScheduledEmails table.
    while True: # Infinite loop, will iterate through following sequence until manually terminated with a KeyboardInterrupt.
        scheduled = ScheduledEmails.query.order_by(ScheduledEmails.send_time).limit(10).all() # Returns first 10 records of ScheduledEmails table, ordered by descending send_time.
        for e in scheduled:
            utcnow = datetime.datetime.utcnow() # Assigns datetime value of current UTC datetime.
            now_time = utcnow.year, utcnow.month, utcnow.day, utcnow.hour, utcnow.minute # Parses utcnow to a resolution of 1 minute.
            send_time = e.send_time.year, e.send_time.month, e.send_time.day, e.send_time.hour, e.send_time.minute # Parses ScheduledEmails record's send_time to a resolution of 1 minute.
            if send_time == now_time: # Checks to see if, given a resolution of 1 minute, UTC now is equal to the send time of the scheduled email.
                if e.sent == False: # Validation check to ensure the scheduled email record has not been previously sent (which may occur if error in deleting record).
                    e.sent = True # Sets sent field of ScheduledEmails record to True, to signify that the email has been sent (to avoid repeatedly sending the same email).
                    db.session.commit() # Commits database object changes to the database.
                    send_phishing_email(e.staff, e.template) # Invokes the send_email() function to create a background thread of the mail.send() method, sending the email to the staff member.
                    print("Email sent", e.staff, e.staff_email, e.send_time) # Prints message to the CLI (command-line) to acknowledge email has been sent - for debugging purposes.
                    db.session.delete(e) # Deletes scheduled email record to avoid data redundancy. The scheduler will not schedule an email automatically if one is already scheduled.
                    db.session.commit()
                else: # If the email has already been tagged as sent, it is deleted and skipped.
                    db.session.delete(e)
                    db.session.commit()
                    continue
            else: # If the scheduled email is not due to be sent, it is skipped, and the next scheduled email record in the list is checked.
                continue