from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, IntegerField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, ValidationError
from models import User, Admin

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=20)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6)
    ])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators=extra_validators):
            return False
            
        # Check if user exists
        user = User.query.filter_by(username=self.username.data).first()
        admin = Admin.query.filter_by(username=self.username.data).first()
        
        if not user and not admin:
            self.username.errors.append('Invalid username')
            return False
            
        # Check password
        if user and not user.check_password(self.password.data):
            self.password.errors.append('Invalid password')
            return False
        if admin and not admin.check_password(self.password.data):
            self.password.errors.append('Invalid password')
            return False
            
        return True

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=20)
    ])
    name = StringField('Full Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6)
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password')
    ])
    submit = SubmitField('Create Account')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')

class ParkingLotForm(FlaskForm):
    name = StringField('Location Name', validators=[DataRequired()])
    location = StringField('Address', validators=[DataRequired()])
    total_spots = IntegerField('Total Spots', validators=[DataRequired(), NumberRange(min=1)])
    rate_per_hour = FloatField('Rate per Hour', validators=[DataRequired(), NumberRange(min=0.1)])
    pincode = StringField('Pincode', validators=[DataRequired(), Length(min=5, max=10)])
    submit = SubmitField('Submit')

class EditUserForm(FlaskForm):
    full_name = StringField('Full Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    address = StringField('Address', validators=[
        Length(min=5, max=200)
    ])
    pincode = StringField('Pincode', validators=[
        Length(min=5, max=10)
    ])
    submit = SubmitField('Save Changes')
