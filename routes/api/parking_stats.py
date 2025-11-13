from flask import jsonify
from ..api import api_bp
from models import db, ParkingLot, ParkingSpot
from sqlalchemy import func, case

@api_bp.route('/parking_stats')
def api_parking_stats():
    stats = db.session.query(
        ParkingLot.prime_location_name,
        func.count(ParkingSpot.id).label('total_spots'),
        func.sum(case((ParkingSpot.status == 'O', 1), else_=0)).label('occupied_spots')
    ).join(
        ParkingSpot, ParkingLot.id == ParkingSpot.lot_id
    ).group_by(
        ParkingLot.id
    ).all()
        
    return jsonify({
        'success': True,
        'data': [{
            'lot_name': stat[0],
            'total_spots': stat[1],
            'occupied_spots': stat[2],
            'available_spots': stat[1] - stat[2]
        } for stat in stats]
    })
        
