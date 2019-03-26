from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo

class AdminLoginForm(FlaskForm): # AdminLoginForm class defined, inherits from FlaskForm superclass. Used for admin logins on the system administrator login page.
    username = StringField('Username', validators=[DataRequired()]) # Represents <input type="text">, first argument is the rendered field name, and the second argument means the field is required
    password = PasswordField('Password', validators=[DataRequired()]) # PasswordField is a StringField but represents <input type="password"> meaning field content is hidden during entry
    submit = SubmitField('Sign In') # Represents <input type="submit">, the only argument is the rendered field name (i.e. the text rendered on the form submit button)

class AdminRegistrationForm(FlaskForm): # Used for system administrator registration.
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')]) # EqualTo validator compares password2 field to password field, valid only if they are equal
    submit = SubmitField('Register')