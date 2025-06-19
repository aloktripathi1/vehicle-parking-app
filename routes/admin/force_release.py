from datetime import datetime
from flask import jsonify, request, session
from flask_login import login_required, current_user
from ..admin import admin_bp
from models import db, Reservation, ParkingSpot

@admin_bp.route('/force_release/<int:reservation_id>', methods=['POST'])
@login_required
def force_release(reservation_id):
    if session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': 'Access denied'})
    
    try:
        reservation = Reservation.query.get_or_404(reservation_id)
        spot = ParkingSpot.query.get(reservation.spot_id)
        
        if not spot:
            return jsonify({
                'success': False,
                'message': 'Parking spot not found'
            })
        
        now = datetime.utcnow()
        duration = now - reservation.parking_timestamp
        hours = duration.total_seconds() / 3600
        
        cost_per_hour = spot.lot.cost_per_hour
        parking_cost = round(hours * cost_per_hour, 2)
        
        reservation.leaving_timestamp = now
        reservation.parking_cost = parking_cost
        reservation.status = 'force_released'
        reservation.force_released = True
        
        spot.status = 'A'
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Reservation force released successfully',
            'cost': parking_cost, 'duration': f"{int(hours)}h {int((hours % 1) * 60)}m"
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})