from flask import jsonify, request, session
from flask_login import login_required, current_user
from ..admin import admin_bp
from models import db, User
from sqlalchemy import or_

@admin_bp.route('/users/search')
@login_required
def search_users():
    if session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': 'Access denied'})
    
        query = request.args.get('q', '')
        if not query:
            return jsonify({'success': True, 'data': []})
        
        users = User.query.filter(
            or_(
                User.name.ilike(f'%{query}%'),
                User.username.ilike(f'%{query}%'),
                User.email.ilike(f'%{query}%')
            )
        ).limit(10).all()
        
        return jsonify({
            'success': True,
            'data': [{
                'id': user.id,
                'name': user.name,
                'username': user.username,
                'email': user.email,
                'address': user.address,
                'pincode': user.pincode
            } for user in users]
        })
        