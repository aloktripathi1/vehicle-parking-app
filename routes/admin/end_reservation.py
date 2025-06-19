from datetime import datetime
from flask import jsonify, request, session, redirect, url_for, flash
from flask_login import login_required, current_user
from ..admin import admin_bp
from models import db, ParkingSpot, Reservation
from utils import format_ist_datetime

@admin_bp.route('/end_reservation/<int:spot_id>', methods=['POST'])
@login_required
def end_reservation(spot_id):
    if session.get('user_type') != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    try:
        spot = ParkingSpot.query.get_or_404(spot_id)
        reservation = Reservation.query.filter_by(
            spot_id=spot_id,
            leaving_timestamp=None
        ).first()
        
        if not reservation:
            flash('No active reservation found for this spot', 'danger')
            return redirect(url_for('admin.occupied_spots'))
        
        now = datetime.utcnow()
        duration = now - reservation.parking_timestamp
        hours = duration.total_seconds() / 3600
        
        cost_per_hour = spot.parking_lot.price  # Using price from parking_lot
        parking_cost = round(hours * cost_per_hour, 2)
        
        reservation.leaving_timestamp = now
        reservation.parking_cost = parking_cost
        reservation.status = 'completed'
        
        spot.status = 'A'
        
        db.session.commit()
        
        end_time = format_ist_datetime(now)
        flash(f'Reservation ended at {end_time}. Cost: ₹{parking_cost}', 'success')
        return redirect(url_for('admin.occupied_spots'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error ending reservation: {str(e)}', 'danger')
        return redirect(url_for('admin.occupied_spots')) 