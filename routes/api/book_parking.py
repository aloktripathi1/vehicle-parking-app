from datetime import datetime
from flask import jsonify, request
from flask_login import login_required, current_user
from ..api import api_bp
from models import db, ParkingSpot, Reservation

@api_bp.route('/book-parking', methods=['POST'])
@login_required
def book_parking():
    try:
        spot_id = request.json.get('spot_id')
        if not spot_id:
            return jsonify({'success': False, 'message': 'No spot selected'})
        
        spot = ParkingSpot.query.get(spot_id)
        if not spot:
            return jsonify({'success': False, 'message': 'Invalid spot'})
        
        if spot.status != 'A':
            return jsonify({'success': False, 'message': 'Spot is not available'})
        
        active_booking = Reservation.query.filter_by(
            user_id=current_user.id,
            leaving_timestamp=None
        ).first()
        
        if active_booking:
            return jsonify({
                'success': False,
                'message': 'You already have an active booking'
            })
        
        reservation = Reservation(
            user_id=current_user.id,
            spot_id=spot.id,
            parking_timestamp=datetime.utcnow(),
            status='active'
        )
        
        spot.status = 'O'
        db.session.add(reservation)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Spot booked successfully',
            'data': {
                'reservation_id': reservation.id,
                'lot_name': spot.lot.prime_location_name,
                'spot_number': spot.spot_number,
                'parking_timestamp': reservation.parking_timestamp.isoformat()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}) 