from flask import render_template, redirect, url_for, flash, session
from flask_login import login_user
from ..main import main_bp
from models import db, User
from forms import RegisterForm

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user = User(
                email=form.email.data,
                name=form.name.data,
                address='', 
                pincode=''  
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            
            login_user(user)
            session['user_type'] = 'user'
            flash('Registration successful! Welcome to ParkEase.', 'success')
            return redirect(url_for('user.user_dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            return render_template('register.html', form=form)
            
    return render_template('register.html', form=form) 