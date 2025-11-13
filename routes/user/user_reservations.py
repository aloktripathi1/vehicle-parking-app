from flask import jsonify
from flask_login import login_required, current_user
from ..user import user_bp
from models import db, Reservation, ParkingSpot, ParkingLot

@user_bp.route('/user/<int:user_id>/reservations')
@login_required
def api_user_reservations(user_id):
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
            'data': [{
                'id': r[0].id,
                'lot_name': r[2].prime_location_name,
                'spot_number': r[1].spot_number,
                'parking_timestamp': r[0].parking_timestamp.isoformat() if r[0].parking_timestamp else None,
                'leaving_timestamp': r[0].leaving_timestamp.isoformat() if r[0].leaving_timestamp else None,
                'status': r[0].status,
                'cost': float(r[0].parking_cost) if r[0].parking_cost else None
            } for r in reservations]
        })
        