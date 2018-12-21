from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, IntegerField, DateTimeField
from wtforms.validators import ValidationError, DataRequired, Length, Email
from app.models import Staff, Departments

#############
# https://gist.github.com/tachyondecay/6016d32f65a996d0d94f

import datetime

from wtforms import Form
from wtforms.fields.html5 import DateField
from wtforms.widgets.html5 import TimeInput

class TimeField(StringField):
    """HTML5 time input."""
    widget = TimeInput()

    def __init__(self, label=None, validators=None, format='%H:%M:%S', **kwargs):
        super(TimeField, self).__init__(label, validators, **kwargs)
        self.format = format

    def _value(self):
        if self.raw_data:
            return ' '.join(self.raw_data)
        else:
            return self.data and self.data.strftime(self.format) or ''

    def process_formdata(self, valuelist):
        if valuelist:
            time_str = ' '.join(valuelist)
            try:
                components = time_str.split(':')
                hour = 0
                minutes = 0
                seconds = 0
                if len(components) in range(2,4):
                    hour = int(components[0])
                    minutes = int(components[1])

                    if len(components) == 3:
                        seconds = int(components[2])
                else:
                    raise ValueError
                self.data = datetime.time(hour, minutes, seconds)
            except ValueError:
                self.data = None
                raise ValueError(self.gettext('Not a valid time string'))

#############

class StaffForm(FlaskForm):
    staff_name = StringField('Staff Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    department = SelectField('Department', coerce=int, validators=[DataRequired()]) # coerce keyword arg says use int() to coerce form data
    submit = SubmitField('Add Staff')

    def validate_email(self, email):
        staff = Staff.query.filter_by(email=email.data).first()
        if staff is not None:
            raise ValidationError('Please use a different email address.')

class SendEmail(FlaskForm):
    selection = SelectField('Select Email Template', choices=[('office', 'Office365'), ('dropbox', 'Dropbox'), ('google', 'Google')])
    submit = SubmitField('Send Phishing Email')

class ScheduleEmail(FlaskForm):
    selection = SelectField('Select Email Template', choices=[('office', 'Office365'), ('dropbox', 'Dropbox'), ('google', 'Google')])
    date_field = DateField('Select Send Date')
    time_field = TimeField('Select Send Time')

    # Use this property to get/set the values of the date and time fields 
    # using a single datetime from an object, e.g., in a form's `__init__` method.
    @property
    def datetime(self):
        if self.date_field.data and self.time_field.data:
            return datetime.datetime.combine(self.date_field.data, self.time_field.data)

    @datetime.setter
    def datetime(self, value):
        self.date_field.data = value.date()
        self.time_field.data = value.time()
    #send_time = DateTimeField('Select Send Date and Time (DD/MM/YYYY HH:MM:SS)', format='%d-%m-%Y %H:%M')
    submit = SubmitField('Schedule Phishing Email')

class LandingPage(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Sign in')

class RemoveStaffForm(FlaskForm):
    submit = SubmitField('Remove Staff Member')

class EditStaffForm(FlaskForm):
    staff_name = StringField('Update Staff Name', validators=[DataRequired()])
    email = StringField('Update Email', validators=[DataRequired(), Email()])
    department = SelectField('Update Department', coerce=int, validators=[DataRequired()])
    risk_score = IntegerField('Update Average Risk Score')
    submit = SubmitField('Submit Detail Changes')

class ResetRiskScoreForm(FlaskForm):
    submit = SubmitField('Reset Risk Score Details')