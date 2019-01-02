from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired

class SearchStaffForm(FlaskForm):
    staff_name = StringField('Staff Name', validators=[DataRequired()])
    submit = SubmitField('Search Staff')

class SearchDepartmentForm(FlaskForm):
    department = SelectField('Department', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Search Department')