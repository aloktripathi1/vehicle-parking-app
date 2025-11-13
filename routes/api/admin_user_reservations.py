from flask import jsonify, session
from flask_login import login_required, current_user
from ..api import api_bp
from models import db, User, Reservation, ParkingSpot, ParkingLot
from utils import format_ist_datetime

@api_bp.route('/admin/user/<int:user_id>/reservations')
@login_required
def admin_user_reservations(user_id):
    if session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': 'Access denied'})
    
    user = User.query.get_or_404(user_id)
        
    reservations = db.session.query(
        Reservation, ParkingSpot, ParkingLot
    ).join(
        ParkingSpot, Reservation.spot_id == ParkingSpot.id
    ).join(
        ParkingLot, ParkingSpot.lot_id == ParkingLot.id
    ).filter(
        Reservation.user_id == user_id
    ).order_by(
        Reservation.parking_timestamp.desc()
    ).all()
        
    return jsonify({
        'success': True,
        'data': {
            'user': {
                'id': user.id,
                'name': user.name,
                'username': user.username,
                'email': user.email
            },
            'reservations': [{
                'id': r[0].id,
                'lot_name': r[2].prime_location_name,
                'spot_number': r[1].spot_number,
                'parking_timestamp': format_ist_datetime(r[0].parking_timestamp),
                'leaving_timestamp': format_ist_datetime(r[0].leaving_timestamp),
                'status': r[0].status,
                'cost': float(r[0].parking_cost) if r[0].parking_cost else None
            } for r in reservations]
        }
    })
        
