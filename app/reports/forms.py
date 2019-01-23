from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, IntegerField
from wtforms.validators import DataRequired, NumberRange

class SearchStaffForm(FlaskForm):
    staff_name = StringField('Staff Name', validators=[DataRequired()])
    submit = SubmitField('Search Staff')

class SearchDepartmentForm(FlaskForm):
    department = SelectField('Department', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Search Department')

class SearchRiskScoreForm(FlaskForm):
    risk_score = IntegerField('Filter by Risk Score', validators=[DataRequired('Input must be a positive integer.'), NumberRange(0, 100, 'Risk score must be between 0 and 100.')])
    submit = SubmitField('Search Staff')