from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_required, current_user
from models import db, User, ParkingLot, ParkingSpot, Reservation
from forms import EditUserForm
from datetime import datetime
import math
from app.user import bp
from app.utils.helpers import has_active_booking

def user_required(f):
    def decorated_function(*args, **kwargs):
        if session.get('user_type') != 'user':
            flash('Access denied', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@bp.route('/dashboard')
@login_required
@user_required
def dashboard():
    try:
        # Get user's active reservation if any
        active_reservation = db.session.query(
            Reservation, ParkingSpot, ParkingLot
        ).join(
            ParkingSpot, Reservation.spot_id == ParkingSpot.id
        ).join(
            ParkingLot, ParkingSpot.lot_id == ParkingLot.id
        ).filter(
            Reservation.user_id == current_user.id,
            Reservation.leaving_timestamp == None
        ).first()
        
        # Get user's past reservations
        past_reservations = db.session.query(
            Reservation, ParkingSpot, ParkingLot
        ).join(
            ParkingSpot, Reservation.spot_id == ParkingSpot.id
        ).join(
            ParkingLot, ParkingSpot.lot_id == ParkingLot.id
        ).filter(
            Reservation.user_id == current_user.id,
            Reservation.leaving_timestamp != None
        ).order_by(Reservation.parking_time.desc()).all()
        
        # Calculate total spent
        total_spent = sum(float(r[0].parking_cost or 0.0) for r in past_reservations)
        
        # Calculate total time spent
        total_time_spent = sum(
            (r[0].leaving_timestamp - r[0].parking_time).total_seconds() / 3600
            for r in past_reservations
        )
        total_time_spent = f"{int(total_time_spent)} hours"
        
        # Prepare chart data
        chart_data = {
            'labels': [],
            'costs': []
        }
        
        if past_reservations:
            chart_data['labels'] = [r[0].parking_time.strftime('%Y-%m-%d') for r in past_reservations[-5:]]
            chart_data['costs'] = [float(r[0].parking_cost or 0.0) for r in past_reservations[-5:]]
        
        return render_template('user/user_dashboard.html',
                            active_reservation=active_reservation,
                            past_reservations=past_reservations,
                            chart_data=chart_data,
                            total_spent=total_spent,
                            total_time_spent=total_time_spent,
                            reservation_history=past_reservations)
    except Exception as e:
        flash(f'An error occurred while loading the dashboard: {str(e)}', 'danger')
        return redirect(url_for('main.index'))

@bp.route('/parking_lots')
@login_required
@user_required
def parking_lots():
    parking_lots = ParkingLot.query.all()
    available_spots = {}
    available_spot_ids = {}
    for lot in parking_lots:
        spots = ParkingSpot.query.filter_by(lot_id=lot.id, is_available=True).all()
        available_spots[lot.id] = len(spots)
        available_spot_ids[lot.id] = [spot.id for spot in spots]
    return render_template(
        'user/user_parking_lots.html',
        parking_lots=parking_lots,
        available_spots=available_spots,
        available_spot_ids=available_spot_ids
    )

@bp.route('/book_spot', methods=['POST'])
@login_required
@user_required
def book_spot():
    try:
        lot_id = request.form.get('lot_id')
        vehicle_number = request.form.get('vehicle_number')
        spot_id = request.form.get('spot_id')
        
        if not lot_id or not vehicle_number:
            return jsonify({'error': 'Missing required fields'}), 400
            
        # Check if user already has an active booking
        if has_active_booking(current_user.id):
            return jsonify({'error': 'You already have an active booking'}), 400
            
        # Get an available spot
        spot = None
        if spot_id:
            spot = ParkingSpot.query.get(spot_id)
            if not spot or not spot.is_available or spot.lot_id != int(lot_id):
                return jsonify({'error': 'Selected spot is not available'}), 400
        else:
            # Find first available spot in the lot
            spot = ParkingSpot.query.filter_by(lot_id=lot_id, is_available=True).first()
            if not spot:
                return jsonify({'error': 'No spots available in this lot'}), 400
        
        # Create reservation
        reservation = Reservation(
            user_id=current_user.id,
            spot_id=spot.id,
            vehicle_number=vehicle_number,
            parking_time=datetime.utcnow()
        )
        
        # Update spot availability
        spot.is_available = False
        
        db.session.add(reservation)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Spot booked successfully!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/vacate_spot/<int:reservation_id>', methods=['POST'])
@login_required
def vacate_spot(reservation_id):
    """Handle vacating a parking spot."""
    try:
        # Get the reservation
        reservation = Reservation.query.get_or_404(reservation_id)
        print(f"Processing vacate request for reservation {reservation_id}")
        
        # Verify ownership
        if reservation.user_id != current_user.id:
            print(f"Unauthorized access attempt: user {current_user.id} tried to vacate reservation {reservation_id}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': 'Unauthorized access'}), 403
            flash('Unauthorized access', 'danger')
            return redirect(url_for('user.dashboard'))
        
        # Update spot status
        spot = reservation.parking_spot
        if not spot:
            print(f"Parking spot not found for reservation {reservation_id}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': 'Parking spot not found'}), 404
            flash('Parking spot not found', 'danger')
            return redirect(url_for('user.dashboard'))
            
        spot.is_available = True
        spot.current_vehicle = None
        
        # Update reservation
        reservation.end_time = datetime.utcnow()
        reservation.status = 'completed'
        
        db.session.commit()
        print(f"Successfully vacated spot for reservation {reservation_id}")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'message': 'Parking spot vacated successfully!'
            })
            
        flash('Parking spot vacated successfully!', 'success')
        return redirect(url_for('user.dashboard'))
        
    except Exception as e:
        db.session.rollback()
        print(f"Error vacating spot: {str(e)}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False,
                'error': 'An error occurred while vacating the spot. Please try again.'
            }), 500
            
        flash('An error occurred while vacating the spot. Please try again.', 'danger')
        return redirect(url_for('user.dashboard'))

@bp.route('/edit_profile', methods=['POST'])
@login_required
@user_required
def edit_profile():
    try:
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        address = request.form.get('address')
        pincode = request.form.get('pincode')
        
        # Validate required fields
        if not all([name, email, address, pincode]):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': False,
                    'message': 'All fields are required'
                }), 400
            flash('All fields are required', 'danger')
            return redirect(url_for('user.dashboard'))
        
        # Update user data
        current_user.name = name
        current_user.email = email
        current_user.address = address
        current_user.pincode = pincode
        
        db.session.commit()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'message': 'Profile updated successfully!'
            })
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user.dashboard'))
        
    except Exception as e:
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False,
                'message': f'Error updating profile: {str(e)}'
            }), 500
        
        flash(f'Error updating profile: {str(e)}', 'danger')
        return redirect(url_for('user.dashboard'))

@bp.route('/search_lots', methods=['POST'])
@login_required
@user_required
def search_lots():
    try:
        query = request.form.get('query', '').strip()
        if not query:
            return redirect(url_for('user.parking_lots'))
        
        # Search in both location name and address
        lots = ParkingLot.query.filter(
            db.or_(
                ParkingLot.prime_location_name.ilike(f'%{query}%'),
                ParkingLot.address.ilike(f'%{query}%')
            )
        ).all()
        
        return render_template('user/user_parking_lots.html', lots=lots, search_query=query)
    except Exception as e:
        flash(f'Error searching lots: {str(e)}', 'danger')
        return redirect(url_for('user.parking_lots'))

@bp.route('/api/parking-lots')
@login_required
@user_required
def api_parking_lots():
    lots = ParkingLot.query.all()
    data = []
    for lot in lots:
        spots = ParkingSpot.query.filter_by(lot_id=lot.id, is_available=True).all()
        data.append({
            'id': lot.id,
            'name': lot.name,
            'location': lot.location,
            'pincode': lot.pincode,
            'price_per_hour': lot.rate_per_hour,
            'available_spots': len(spots),
            'spot_ids': [spot.id for spot in spots]
        })
    return jsonify(data) 