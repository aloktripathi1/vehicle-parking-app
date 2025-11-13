from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from ..user import user_bp
from models import db

@user_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if session.get('user_type') != 'user':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        try:
            current_user.name = request.form.get('name')
            current_user.email = request.form.get('email')
            current_user.address = request.form.get('address')
            current_user.pincode = request.form.get('pincode')
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return {'success': True, 'message': 'Profile updated successfully!'}
            return redirect(url_for('user.user_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating profile', 'danger')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return {'success': False, 'message': 'An error occurred while updating profile'}
    
    return render_template('user/edit_profile.html', user=current_user) 