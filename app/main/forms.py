from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Length, Email
from app.models import Staff, Departments

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
    selection = SelectField('Select an email', choices=[('office', 'Office365'), ('dropbox', 'Dropbox'), ('google', 'Google')])
    submit = SubmitField('Send Phishing Email')

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