import datetime, time, random
from phishing import app # app is the INSTANCE
from app import db # from app DIRECTORY
from app.models import Staff, ScheduledEmails

templates = ['office', 'dropbox', 'google', 'anonymous'] # List of available email templates.

def schedule_email(staff, days, templates): # Function defined to select a random email template from the list above, a random send_time in the next 'days' (argument) days,
                                            # and return a ScheduledEmails record object to be sent to 'staff' (argument) instantiated with these arguments.
    template = templates[random.randrange(len(templates) - 1)] # Selects random email template from list of templates.
    send_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=random.randrange(24 * 60 * 60 * days)) # Selects random send time over the next 'days' number of days.
    scheduled_email = ScheduledEmails(staff_email=staff.email, template=template, send_time=send_time, staff=staff) # Instantiates ScheduledEmails record
    return scheduled_email

with app.app_context(): # Requires application context to access the database and modify the contents of the ScheduledEmails table.
    while True: # Infinite loop, will iterate through following sequence until manually terminated with a KeyboardInterrupt.
        print("----------\nScheduling ", datetime.datetime.utcnow().replace(microsecond=0)) # Prints message to CLI (command-line) to signify the start of a scheduler iteration - for debugging purposes.
        for staff in Staff.query.all(): # Iterates through all staff records in the Staff table of the database.
            if (((datetime.datetime.utcnow() - staff.last_sent).days) >= 7) and (staff.direction == False) and (len(list(staff.scheduled_emails)) == 0): # Returns True if it has been 7 days since email last sent to staff member,
                                                                                                                                                         # they are an increasing risk, and have no emails already scheduled.
                scheduled_email = schedule_email(staff, 3, templates) # Returns ScheduledEmails object, with send time set as a random time over the next 3 days.
                db.session.add(scheduled_email) # Adds new ScheduledEmails record to the database.
                print("Email scheduled 1", staff.email, scheduled_email.send_time) # Prints message to CLI (command-line) to identify which of the 3 conditional statements scheduled the email, and what time the email is scheduled to be sent - for debugging purposes.
            elif (((datetime.datetime.utcnow() - staff.last_sent).days) >= 7) and (staff.risk_score >= 50) and (len(list(staff.scheduled_emails)) == 0): # Returns True if it has been 7 days since email last sent to staff member,
                                                                                                                                                         # they have a risk score greater than or equal to 50, and have no emails already scheduled.
                scheduled_email = schedule_email(staff, 3, templates)
                db.session.add(scheduled_email)
                print("Email scheduled 2", staff.email, scheduled_email.send_time)
            elif ((datetime.datetime.utcnow() - staff.last_sent).days) >= 30 and (len(list(staff.scheduled_emails)) == 0): # Returns True if it has been 30 days since email last sent to staff member, and have no emails
                                                                                                                           # already scheduled. This way an email is scheduled for each staff member at least once per month.
                scheduled_email = schedule_email(staff, 3, templates)
                db.session.add(scheduled_email)
                print("Email scheduled 3", staff.email, scheduled_email.send_time)
        db.session.commit() # Commits database changes to the database.
        time.sleep(1800) # Suspends the execution of the loop for 1800 seconds (30 minutes), meaning the scheduler only checks if emails need to be scheduled every 30 minutes.


################ TO BE USED FOR SCHEDULER TESTING ################
# templates = ['office', 'dropbox', 'google', 'anonymous'] # List of available email templates.

# def schedule_email(staff, minutes, templates): # Function defined to select a random email template from the list above, a random send_time in the next 'days' (argument) days,
#                                             # and return a ScheduledEmails record object to be sent to 'staff' (argument) instantiated with these arguments.
#     template = templates[random.randrange(len(templates) - 1)] # Selects random email template from list of templates.
#     send_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=random.randrange(60 * minutes)) # Selects random send time over the next 'days' number of days.
#     scheduled_email = ScheduledEmails(staff_email=staff.email, template=template, send_time=send_time, staff=staff) # Instantiates ScheduledEmails record
#     return scheduled_email

# with app.app_context(): # Requires application context to access the database and modify the contents of the ScheduledEmails table.
#     while True: # Infinite loop, will iterate through following sequence until manually terminated with a KeyboardInterrupt.
#         print("----------\nScheduling ", datetime.datetime.utcnow().replace(microsecond=0)) # Prints message to CLI (command-line) to signify the start of a scheduler iteration - for debugging purposes.
#         for staff in Staff.query.all(): # Iterates through all staff records in the Staff table of the database.
#             if (((datetime.datetime.utcnow() - staff.last_sent).seconds) >= 180) and (staff.direction == False) and (len(list(staff.scheduled_emails)) == 0): # Returns True if it has been 7 days since email last sent to staff member,
#                                                                                                                                                          # they are an increasing risk, and have no emails already scheduled.
#                 scheduled_email = schedule_email(staff, 5, templates) # Returns ScheduledEmails object, with send time set as a random time over the next 3 days.
#                 db.session.add(scheduled_email) # Adds new ScheduledEmails record to the database.
#                 print("Email scheduled 1", staff.email, scheduled_email.send_time) # Prints message to CLI (command-line) to identify which of the 3 conditional statements scheduled the email, and what time the email is scheduled to be sent - for debugging purposes.
#             elif (((datetime.datetime.utcnow() - staff.last_sent).seconds) >= 180) and (staff.risk_score >= 50) and (len(list(staff.scheduled_emails)) == 0): # Returns True if it has been 7 days since email last sent to staff member,
#                                                                                                                                                          # they have a risk score greater than or equal to 50, and have no emails already scheduled.
#                 scheduled_email = schedule_email(staff, 5, templates)
#                 db.session.add(scheduled_email)
#                 print("Email scheduled 2", staff.email, scheduled_email.send_time)
#             elif ((datetime.datetime.utcnow() - staff.last_sent).seconds) >= 420 and (len(list(staff.scheduled_emails)) == 0): # Returns True if it has been 30 days since email last sent to staff member, and have no emails
#                                                                                                                            # already scheduled. This way an email is scheduled for each staff member at least once per month.
#                 scheduled_email = schedule_email(staff, 5, templates)
#                 db.session.add(scheduled_email)
#                 print("Email scheduled 3", staff.email, scheduled_email.send_time)
#         db.session.commit() # Commits database changes to the database.
#         time.sleep(60) # Suspends the execution of the loop for 1800 seconds (30 minutes), meaning the scheduler only checks if emails need to be scheduled every 30 minutes.
##########################################