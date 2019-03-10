from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, IntegerField, DateTimeField
from wtforms.validators import ValidationError, DataRequired, Length, Email, NumberRange
from app.models import Staff, Departments

# Flask WTForms does not provide a DateTime form field with HTML5 rendering. Instead, the field renders as a text field with very strict validators regarding
# how the datetime data must be inputted into the field entry. Therefore, I chose to instead import a file from GitHub that uses the DateField and TimeInput provided
# by WTForms to create a TimeField. Using the DateField and TimeField to act as a DateTimeField, the two inputs are concatenated to form a datetime data type.
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

class StaffForm(FlaskForm): # StaffForm class defined, inherits from FlaskForm superclass. Used by the system administrator for adding a staff member to the database on the index page.
    staff_name = StringField('Staff Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    department = SelectField('Department', coerce=int, validators=[DataRequired()]) # coerce keyword argument says use int() to coerce form data
    submit = SubmitField('Add Staff')

    # The choices argument is not provided here in the SelectField() instantiation, as it is instead defined on a GET request of the page which renders the StaffForm.
    # The reason for this is that it creates a dynamic drop-down list. In order to do this, the choices list must be assigned after instantiation. Otherwise, if
    # a new department is added whilst the application is running, the application must be restarted in order for it to be shown in the drop-down list. However,
    # with a dynamic drop-down list, the page only needs to be reloaded for the new department to be shown.

    def validate_email(self, email): # Custom validator to ensure each staff member has a unique email address
        staff = Staff.query.filter_by(email=email.data).first() # Query returns the first staff member object if the object's email attribute matches the form entry email, returns None otherwise
        if staff is not None:
            raise ValidationError('Please use a different email address.') # Raises a validation error, with the argument being the exception message shown to the user

    # Any method with the format validate_<field_name> is taken by WTForms as being a custom validator, and they are invoked alongside the stock validators.

class SendEmail(FlaskForm): # SendEmail class defined, inherits from FlaskForm superclass. Used by the system administrator for manually sending a test phishing email to a specific staff member.
    selection = SelectField('Select Email Template', choices=[('office', 'Office365'), ('dropbox', 'Dropbox'), ('google', 'Google')])
    sendSubmit = SubmitField('Send Phishing Email')

class ScheduleEmail(FlaskForm): # Used by the system administrator for manually scheduling a test phishing email to be sent to a specific staff member.
    selection = SelectField('Select Email Template', choices=[('office', 'Office365'), ('dropbox', 'Dropbox'), ('google', 'Google')])
    date_field = DateField('Select Send Date')
    time_field = TimeField('Select Send Time')

############# The datetime method implemented is used to return the DateField and TimeField values as a concatenated datetime data type.
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
#############

    #send_time = DateTimeField('Select Send Date and Time (DD/MM/YYYY HH:MM:SS)', format='%d-%m-%Y %H:%M') # Old field - replaced by imported datetime methods.
    scheduleSubmit = SubmitField('Schedule Phishing Email')

class LandingPage(FlaskForm): # Acts as the fake phishing email landing page submission form. Used to detect if a staff member has submitted data to the test phishing site. No form validation required.
    username = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Sign in')

class RemoveStaffForm(FlaskForm): # Used by the system administrator to remove a staff member from the database upon submission of this form.
    removeSubmit = SubmitField('Remove Staff Member')

class EditStaffForm(FlaskForm): # Used by the system administrator to edit a specific staff member's profile details.
    staff_name = StringField('Update Staff Name', validators=[DataRequired()])
    email = StringField('Update Email', validators=[DataRequired(), Email()]) # Represents <input type="text">, first argument is the rendered field name, and the second argument means
                                                                              # the field is required and the entry validates as an email address format (makes use of primitive regular expression)
    department = SelectField('Update Department', coerce=int, validators=[DataRequired()])
    risk_score = IntegerField('Update Average Risk Score', validators=[DataRequired('Input must be a positive integer.'), NumberRange(0, 100, 'Risk score must be between 0 and 100.')]) # NumberRange validates input integer is between 0 and 100, as that is the possible risk score range. Third argument for this validator is the error message.
    editSubmit = SubmitField('Submit Detail Changes')

class ResetRiskScoreForm(FlaskForm): # Used by the system administrator to reset a staff member's risk score details (no. emails received, risk score, links clicked, etc.) to zero.
    resetSubmit = SubmitField('Reset Risk Score Details')