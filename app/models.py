from app import db

class Departments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department_name = db.Column(db.String(64), index=True, unique=True)
    risk_score = db.Column(db.Integer, default=0)
    staff_members = db.relationship('Staff', backref='department', lazy='dynamic')

    def __repr__(self):
        return '<Department {}>'.format(self.department_name)

class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True) # nullable=False is implied with primary key
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id')) # departments is the name of the database table, NOT the model (hence lowercase 'd') *however by default this is model name*
    staff_name = db.Column(db.String(64), index=True, unique=False) # check documentation on 'nullable' - makes sense
    email = db.Column(db.String(120), index=True, unique=True)
    clicked = db.Column(db.Integer, default=0)
    submitted = db.Column(db.Integer, default=0)
    delivered = db.Column(db.Integer, default=0)
    risk_score = db.Column(db.Integer, default=0)
    scheduled_emails = db.relationship('ScheduledEmails', backref='staff', lazy='dynamic') # notice uppercase 'S' for Scheduled (name of MODEL)
    # for one-to-many relationship, relationship defined on 'one' side... not a part of database diagram... it just defines the relationship
    # backref allows staff to be found given a scheduled email (ScheduledEmails.staff) - useful for reports
    # lazy defines how database query for relationship  will be issued (dynamic just means it returns an object, basically)

    def __repr__(self):
        return '<Staff {}>'.format(self.staff_name)

class ScheduledEmails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'))
    staff_email = db.Column(db.String(120), index=True, nullable=False) # not unique, as could be multiple scheduled for same staff member  
    template = db.Column(db.String(30), nullable=False) # template of email to be sent
    send_time = db.Column(db.DateTime, index=True, nullable=False)
    sent = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<ScheduledEmail {}>'.format(self.staff_email)