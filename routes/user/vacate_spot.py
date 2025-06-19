from datetime import datetime
from flask import jsonify, request, flash, redirect, url_for
from flask_login import login_required, current_user
from ..user import user_bp
from models import db, Reservation, ParkingSpot

@user_bp.route('/vacate_spot/<int:reservation_id>', methods=['POST'])
@login_required
def vacate_spot(reservation_id):
    try:
        reservation = Reservation.query.get(reservation_id)
        if not reservation:
            flash('Reservation not found', 'danger')
            return redirect(url_for('user.user_dashboard'))
        
        if reservation.user_id != current_user.id:
            flash('Unauthorized', 'danger')
            return redirect(url_for('user.user_dashboard'))
        
        if reservation.leaving_timestamp:
            flash('Spot already vacated', 'warning')
            return redirect(url_for('user.user_dashboard'))
        
        now = datetime.utcnow()
        duration = now - reservation.parking_timestamp
        hours = duration.total_seconds() / 3600
        
        spot = ParkingSpot.query.get(reservation.spot_id)
        if not spot:
            flash('Spot not found', 'danger')
            return redirect(url_for('user.user_dashboard'))
        
        cost_per_hour = spot.parking_lot.price
        parking_cost = round(hours * cost_per_hour, 2)
        print(f"Vacate: spot_id={spot.id}, lot_id={spot.lot_id}, hours={hours}, cost_per_hour={cost_per_hour}, parking_cost={parking_cost}")
        
        reservation.leaving_timestamp = now
        reservation.parking_cost = parking_cost
        reservation.status = 'completed'
        
        spot.status = 'A'
        
        db.session.commit()
        flash('Spot vacated successfully!', 'success')
        return redirect(url_for('user.user_dashboard'))
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while vacating spot', 'danger')
        return redirect(url_for('user.user_dashboard')) 