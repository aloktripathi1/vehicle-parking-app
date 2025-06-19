from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, IntegerField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, ValidationError, Regexp
from models import User, Admin
from werkzeug.security import check_password_hash

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
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
            
        admin = Admin.query.filter_by(email=self.email.data).first()
        if admin and check_password_hash(admin.password_hash, self.password.data):
            return True
            
        user = User.query.filter_by(email=self.email.data).first()
        if user and check_password_hash(user.password_hash, self.password.data):
            return True
            
        self.email.errors.append('Invalid email or password')
        self.password.errors.append('Invalid email or password')
        return False

class RegisterForm(FlaskForm):
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

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')

class ParkingLotForm(FlaskForm):
    prime_location_name = StringField('Location Name', validators=[DataRequired()])
    price = FloatField('Price per Hour', validators=[DataRequired(), NumberRange(min=0.1)])
    address = StringField('Address', validators=[DataRequired()])
    pincode = IntegerField('Pincode', validators=[
        DataRequired(),
        NumberRange(min=100000, max=999999, message='Pincode must be a 6-digit number')
    ])
    max_spots = IntegerField('Maximum Spots', validators=[DataRequired(), NumberRange(min=1)])
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
        DataRequired(),
        Length(min=5, max=200)
    ])
    pincode = StringField('Pincode', validators=[
        DataRequired(),
        Length(min=6, max=6),
        Regexp(r'^\d{6}$', message='Pincode must be a 6-digit number')
    ])
    submit = SubmitField('Save Changes')
