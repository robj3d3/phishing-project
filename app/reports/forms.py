from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, IntegerField
from wtforms.validators import DataRequired, NumberRange

class SearchStaffForm(FlaskForm): # SearchStaffForm class defined, inherits from FlaskForm superclass. Used by the system administrator for querying the Staff table to search for a specific staff member by name.
    staff_name = StringField('Staff Name', validators=[DataRequired()])
    submit = SubmitField('Search Staff')

class SearchDepartmentForm(FlaskForm): # Used by the system administrator for querying the Departments table to search for a specific department by name.
    department = SelectField('Department', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Search Department')

class SearchRiskScoreForm(FlaskForm): # Used by the system administrator for querying the Staff table to search for staff members with a given risk score or higher.
    risk_score = IntegerField('Filter by Risk Score', validators=[DataRequired('Input must be a positive integer.'), NumberRange(0, 100, 'Risk score must be between 0 and 100.')]) # Represents <input type="text">, except all input is coerced to an integer. Erroneous input is ignored and rejected.
    submit = SubmitField('Search Staff')                                                                                                                                            # NumberRange validates input integer is between 0 and 100, as that is the possible risk score range. Third argument is the error message.