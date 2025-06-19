from datetime import datetime
from flask import jsonify, request
from flask_login import login_required, current_user
from ..user import user_bp
from models import db, ParkingSpot, Reservation

@user_bp.route('/book_spot', methods=['POST'])
@login_required
def book_spot():
    try:
        spot_id = request.form.get('spot_id')
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
            return jsonify({'success': False, 'message': 'You already have an active booking'})
        
        reservation = Reservation(
            user_id=current_user.id,
            spot_id=spot.id,
            parking_timestamp=datetime.utcnow(),
            vehicle_number=request.form.get('vehicle_number')
        )
        
        spot.status = 'O'
        db.session.add(reservation)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Spot booked successfully',
            'reservation_id': reservation.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}) 