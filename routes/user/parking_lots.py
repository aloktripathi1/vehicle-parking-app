from flask import render_template, redirect, url_for, flash, session
from flask_login import login_required, current_user
from ..user import user_bp
from models import ParkingLot, ParkingSpot

@user_bp.route('/parking_lots')
@login_required
def user_parking_lots():
    if session.get('user_type') != 'user':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    parking_lots = ParkingLot.query.all()
    available_spots = {}
    available_spot_ids = {}
    for lot in parking_lots:
        spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').all()
        available_spots[lot.id] = len(spots)
        available_spot_ids[lot.id] = [spot.id for spot in spots]
    return render_template('user_parking_lots.html', parking_lots=parking_lots, available_spots=available_spots, available_spot_ids=available_spot_ids) 