from flask import jsonify
from flask_login import login_required, current_user
from ..admin import admin_bp
from models import db, ParkingLot, ParkingSpot, Reservation
from sqlalchemy import func, and_

@admin_bp.route('/parking_lot/<int:lot_id>/spots', methods=['GET'])
@login_required
def get_parking_lot_spots(lot_id):
        lot = ParkingLot.query.get_or_404(lot_id)
        
        spots = db.session.query(
            ParkingSpot,
            func.count(Reservation.id).label('active_reservations')
        ).outerjoin(
            Reservation,
            and_(
                ParkingSpot.id == Reservation.spot_id,
                Reservation.leaving_timestamp.is_(None)
            )
        ).filter(
            ParkingSpot.lot_id == lot_id
        ).group_by(
            ParkingSpot.id
        ).all()
        
        return jsonify({
            'success': True,
            'data': {
                'lot_name': lot.prime_location_name,
                'price': float(lot.price),
                'spots': [{
                    'id': spot[0].id,
                    'status': spot[0].status,
                    'has_active_reservation': spot[1] > 0
                } for spot in spots]
            }
        })
        