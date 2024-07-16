from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, EmailField, BooleanField, FileField, StringField, Form, SelectField
from wtforms.validators import Length, DataRequired, Email, EqualTo

class SiteConfigForm(FlaskForm):
    site_name = StringField('Site Name', validators=[DataRequired(), Length(2, 64)])
    site_allow_registration = BooleanField('Allow Registration')
    submit = SubmitField('Save Changes')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 32)])
    password = PasswordField('Password', validators=[DataRequired(), Length(1, 128)])
    firstname = StringField('First Name', validators=[DataRequired(), Length(1, 32)])
    lastname = StringField('Last Name', validators=[DataRequired(), Length(1, 32)])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 32)])
    password = PasswordField('Password', validators=[DataRequired(), Length(1, 128)])
    submit = SubmitField('Log In')

class ExtensionUploadForm(FlaskForm):
    extension = FileField('Upload Extension', validators=[DataRequired()])
    submit = SubmitField('Upload Extension')

class AvatarUpload(FlaskForm):
    avatar_upload = FileField('Upload Avatar', validators=[DataRequired()])
    submit = SubmitField('Apply')

class UserProfile(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired(), Length(1, 32)])
    lastname = StringField('Last Name', validators=[DataRequired(), Length(1, 32)])
    submit = SubmitField('Save Changes')

class ChangePassword(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired(), Length(1, 128)])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(1, 128)])
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('new_password'), DataRequired(), Length(1, 128)])
    submit = SubmitField('Set New Password')

def ExtensionsCRUD(blueprints: list):
    class Prefs(Form):
        pass
    length = 0
    for blueprint in blueprints:
        setattr(Prefs, blueprint, BooleanField(blueprint))
        length += 1
    setattr(Prefs, 'submit', SubmitField('Apply'))
    setattr(Prefs, 'action_field', SelectField('Action', choices=[('none', 'Bulk Actions'), ('enable', 'Enable'), ('disable', 'Disable'), ('delete', 'Delete')]))
    return Prefs