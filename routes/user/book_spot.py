from datetime import datetime
from flask import jsonify, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from ..user import user_bp
from models import db, ParkingSpot, Reservation, ParkingLot

@user_bp.route('/book_spot/<int:lot_id>', methods=['GET'])
@login_required
def book_spot_page(lot_id):
    """Display booking page for a specific parking lot"""
    # Check if user has complete profile
    if not current_user.address or not current_user.pincode:
        flash('Please complete your profile before booking a parking spot.', 'warning')
        return redirect(url_for('user.edit_profile'))
    
    # Check for active booking
    active_booking = Reservation.query.filter_by(
        user_id=current_user.id,
        leaving_timestamp=None
    ).first()
    
    if active_booking:
        flash('You already have an active booking. Please vacate it before booking a new spot.', 'danger')
        return redirect(url_for('user.user_dashboard'))
    
    # Get parking lot details
    lot = ParkingLot.query.get_or_404(lot_id)
    
    # Get available spots
    available_spots_query = ParkingSpot.query.filter_by(
        parking_lot_id=lot_id,
        status='A'
    ).all()
    
    if not available_spots_query:
        flash('No available spots at this parking lot.', 'warning')
        return redirect(url_for('user.parking_lots'))
    
    # Get first available spot
    spot_id = available_spots_query[0].id
    available_spots = len(available_spots_query)
    
    return render_template('user/book_spot.html', 
                         lot=lot, 
                         spot_id=spot_id,
                         available_spots=available_spots)

@user_bp.route('/book_spot', methods=['POST'])
@login_required
def book_spot():
    spot_id = request.form.get('spot_id')
    if not spot_id:
        flash('No spot selected', 'danger')
        return redirect(url_for('user.parking_lots'))
        
    spot = ParkingSpot.query.get(spot_id)
    if not spot:
        flash('Invalid spot', 'danger')
        return redirect(url_for('user.parking_lots'))
        
    if spot.status != 'A':
        flash('Spot is not available', 'danger')
        return redirect(url_for('user.parking_lots'))
        
    active_booking = Reservation.query.filter_by(
        user_id=current_user.id,
        leaving_timestamp=None
    ).first()
        
    if active_booking:
        flash('You already have an active booking', 'danger')
        return redirect(url_for('user.user_dashboard'))
        
    reservation = Reservation(
        user_id=current_user.id,
        spot_id=spot.id,
        parking_timestamp=datetime.utcnow(),
        vehicle_number=request.form.get('vehicle_number')
    )
        
    spot.status = 'O'
    db.session.add(reservation)
    db.session.commit()
        
    flash('Spot booked successfully!', 'success')
    return redirect(url_for('user.user_dashboard'))
        
