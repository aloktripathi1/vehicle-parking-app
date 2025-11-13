from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required
from ..main import main_bp
from models import User
from forms import LoginForm
from werkzeug.security import check_password_hash

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate():
            admin = Admin.query.filter_by(email=form.email.data).first()
            if admin and check_password_hash(admin.password_hash, form.password.data):
                login_user(admin)
                session['user_type'] = 'admin'
                return redirect(url_for('admin.admin_dashboard'))
            
            user = User.query.filter_by(email=form.email.data).first()
            if user and check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                session['user_type'] = 'user'
                return redirect(url_for('user.user_dashboard'))
            
            flash('Invalid email or password', 'danger')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{field.title()}: {error}', 'danger')
    
    return render_template('main/login.html', form=form)

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('main.index')) 