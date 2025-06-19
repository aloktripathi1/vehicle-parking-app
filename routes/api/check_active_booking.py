from flask import jsonify
from flask_login import login_required, current_user
from ..api import api_bp
from models import db, Reservation, ParkingSpot, ParkingLot

@api_bp.route('/check-active-booking')
@login_required
def check_active_booking():
    try:
        active_reservation = db.session.query(
            Reservation, ParkingSpot, ParkingLot
        ).join(
            ParkingSpot, Reservation.spot_id == ParkingSpot.id
        ).join(
            ParkingLot, ParkingSpot.lot_id == ParkingLot.id
        ).filter(
            Reservation.user_id == current_user.id,
            Reservation.leaving_timestamp.is_(None)
        ).first()
        
        if active_reservation:
            return jsonify({
                'success': True,
                'has_active_booking': True,
                'data': {
                    'reservation_id': active_reservation[0].id,
                    'lot_name': active_reservation[2].prime_location_name,
                    'spot_number': active_reservation[1].spot_number,
                    'parking_timestamp': active_reservation[0].parking_timestamp.isoformat()
                }
            })
        
        return jsonify({'success': True, 'has_active_booking': False})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}) 