from flask import jsonify, request, session
from flask_login import login_required, current_user
from ..admin import admin_bp
from models import db, User
from forms import EditUserForm

@admin_bp.route('/edit_user/<int:user_id>', methods=['POST'])
@login_required
def edit_user(user_id):
    if session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': 'Access denied'})
    
    try:
        user = User.query.get_or_404(user_id)
        form = EditUserForm()
        
        if form.validate_on_submit():
            user.name = form.name.data
            user.email = form.email.data
            user.address = form.address.data
            user.pincode = form.pincode.data
            
            if form.password.data:
                user.set_password(form.password.data)
            
            db.session.commit()
            return jsonify({'success': True, 'message': 'User updated successfully'})
        else:
            return jsonify({'success': False, 'message': 'Invalid form data'})
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}) 