from flask import jsonify, request, session, redirect, url_for, flash
from flask_login import login_required, current_user
from ..admin import admin_bp
from models import db, ParkingLot, ParkingSpot, Reservation

@admin_bp.route('/parking_lot/<int:lot_id>/delete', methods=['POST'])
@login_required
def delete_parking_lot(lot_id):
    if session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': 'Access denied'})
    
    lot = ParkingLot.query.get_or_404(lot_id)
        
    occupied_spots = ParkingSpot.query.filter_by(
        lot_id=lot_id,
        status='O'
    ).first()
        
    if occupied_spots:
        flash('Cannot delete parking lot with occupied spots', 'danger')
        return redirect(url_for('admin.admin_parking_lots'))
        
    spot_ids = [spot.id for spot in ParkingSpot.query.filter_by(lot_id=lot_id).all()]
    if spot_ids:
        Reservation.query.filter(Reservation.spot_id.in_(spot_ids)).delete(synchronize_session=False)
    ParkingSpot.query.filter_by(lot_id=lot_id).delete()
        
    db.session.delete(lot)
    db.session.commit()
        
    flash('Parking lot deleted successfully', 'success')
    return redirect(url_for('admin.admin_parking_lots'))
        
