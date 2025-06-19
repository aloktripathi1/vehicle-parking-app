from flask import jsonify, request, session
from flask_login import login_required, current_user
from ..admin import admin_bp
from models import db, User

@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': 'Access denied'})
    
    try:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'User deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}) 