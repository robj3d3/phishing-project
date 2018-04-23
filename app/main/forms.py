from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Length, Email
from app.models import Staff

class StaffForm(FlaskForm):
    staffname = StringField('Staff Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Add Staff')

    def validate_staffname(self, staffname):
        staff = Staff.query.filter_by(staffname=staffname.data).first()
        if staff is not None:
            raise ValidationError('Please use a different staff name.')

    def validate_email(self, email):
        staff = Staff.query.filter_by(email=email.data).first()
        if staff is not None:
            raise ValidationError('Please use a different email address.')

class SendEmail(FlaskForm):
    submit = SubmitField('Send Phishing Email')