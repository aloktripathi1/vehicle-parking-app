from flask import render_template, redirect, url_for, flash, session
from flask_login import login_required, current_user
from ..admin import admin_bp
from models import db, ParkingSpot, ParkingLot, Reservation, User
import traceback
from datetime import datetime

@admin_bp.route('/occupied_spots')
@login_required
def occupied_spots():
    if session.get('user_type') != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    try:
        occupied_spots_raw = db.session.query(
            ParkingSpot, ParkingLot, Reservation
        ).join(
            Reservation, ParkingSpot.id == Reservation.spot_id
        ).join(
            ParkingLot, ParkingSpot.lot_id == ParkingLot.id
        ).filter(
            Reservation.leaving_timestamp.is_(None)
        ).all()
        
        occupied_spots = []
        for spot, lot, reservation in occupied_spots_raw:
            user = User.query.get(reservation.user_id)
            occupied_spots.append((spot, lot, reservation, user))
            
        now = datetime.utcnow()
        return render_template('admin/admin_occupied_spots.html', occupied_spots=occupied_spots, now=now)
            
    except Exception as e:
        print('Admin occupied spots error:', e)
        traceback.print_exc()
        flash('An error occurred while loading occupied spots', 'danger')
        return redirect(url_for('admin.admin_dashboard')) 