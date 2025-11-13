from flask import jsonify
from flask_login import login_required, current_user
from ..api import api_bp
from models import db, ParkingLot, ParkingSpot
from sqlalchemy import func, case

@api_bp.route('/parking-lots')
@login_required
def api_parking_lots():
    lots = db.session.query(
        ParkingLot,
        func.count(ParkingSpot.id).label('total_spots'),
        func.sum(case((ParkingSpot.status == 'O', 1), else_=0)).label('occupied_spots')
    ).outerjoin(
        ParkingSpot, ParkingLot.id == ParkingSpot.lot_id
    ).group_by(
        ParkingLot.id
    ).all()
        
    return jsonify({
        'success': True,
        'data': [{
            'id': lot[0].id,
            'name': lot[0].prime_location_name,
            'address': lot[0].address,
            'pincode': lot[0].pincode,
            'total_spots': lot[1],
            'occupied_spots': lot[2],
            'available_spots': lot[1] - lot[2]
        } for lot in lots]
    })
        
