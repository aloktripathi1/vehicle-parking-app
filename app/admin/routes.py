from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_required, current_user
from models import db, User, Admin, ParkingLot, ParkingSpot, Reservation
from forms import ParkingLotForm, EditUserForm
from sqlalchemy import func
from datetime import datetime, timedelta
import traceback
import math
from app.admin import bp

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if session.get('user_type') != 'admin':
            flash('Access denied', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    try:
        parking_lots = ParkingLot.query.all()
        total_spots = ParkingSpot.query.count()
        occupied_spots = ParkingSpot.query.filter_by(is_available=False).count()
        available_spots = total_spots - occupied_spots
        users = User.query.count()
        
        # Get today's date at midnight
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday = today - timedelta(days=1)
        
        # Calculate today's revenue
        today_revenue = db.session.query(func.coalesce(func.sum(Reservation.parking_cost), 0.0))\
            .filter(Reservation.leaving_timestamp >= today,
                    Reservation.leaving_timestamp.isnot(None)).scalar() or 0.0
        
        # Calculate yesterday's revenue
        yesterday_revenue = db.session.query(func.coalesce(func.sum(Reservation.parking_cost), 0.0))\
            .filter(Reservation.leaving_timestamp >= yesterday,
                    Reservation.leaving_timestamp < today,
                    Reservation.leaving_timestamp.isnot(None)).scalar() or 0.0
        
        # Calculate revenue change
        revenue_change = today_revenue - yesterday_revenue
        revenue_change_percent = (revenue_change / yesterday_revenue * 100) if yesterday_revenue > 0 else 0
        
        # Calculate new users today
        new_users_today = User.query.filter(User.created_at >= today).count()
        new_users_yesterday = User.query.filter(
            User.created_at >= yesterday,
            User.created_at < today
        ).count()
        
        # Calculate user change
        user_change = new_users_today - new_users_yesterday
        user_change_percent = (user_change / new_users_yesterday * 100) if new_users_yesterday > 0 else 0
        
        # Calculate spot changes
        occupied_spots_yesterday = ParkingSpot.query.filter_by(is_available=False).count()
        spot_change = occupied_spots - occupied_spots_yesterday
        
        # Total revenue calculations
        total_revenue = db.session.query(func.coalesce(func.sum(Reservation.parking_cost), 0.0))\
            .filter(Reservation.leaving_timestamp.isnot(None)).scalar() or 0.0
        
        # Prepare data for charts
        lot_data = []
        for lot in parking_lots:
            # Get revenue for this lot
            lot_revenue = db.session.query(func.coalesce(func.sum(Reservation.parking_cost), 0.0))\
                .join(ParkingSpot, Reservation.spot_id == ParkingSpot.id)\
                .filter(ParkingSpot.lot_id == lot.id,
                        Reservation.leaving_timestamp.isnot(None)).scalar() or 0.0
            
            # Get spot counts
            total_lot_spots = ParkingSpot.query.filter_by(lot_id=lot.id).count()
            occupied_lot_spots = ParkingSpot.query.filter_by(lot_id=lot.id, is_available=False).count()
            
            lot_data.append({
                'name': lot.name or '',
                'revenue': float(lot_revenue),
                'total_spots': int(total_lot_spots),
                'occupied_spots': int(occupied_lot_spots),
                'available_spots': int(total_lot_spots - occupied_lot_spots)
            })
        
        # Prepare chart data
        chart_data = {
            'lot_data': lot_data,
            'total_revenue': float(total_revenue),
            'today_revenue': float(today_revenue),
            'yesterday_revenue': float(yesterday_revenue)
        }
        
        return render_template('admin/admin_dashboard.html',
                            parking_lots=parking_lots,
                            total_spots=total_spots,
                            occupied_spots=occupied_spots,
                            available_spots=available_spots,
                            users=users,
                            today_revenue=today_revenue,
                            yesterday_revenue=yesterday_revenue,
                            revenue_change=revenue_change,
                            revenue_change_percent=revenue_change_percent,
                            new_users_today=new_users_today,
                            user_change=user_change,
                            user_change_percent=user_change_percent,
                            spot_change=spot_change,
                            total_revenue=total_revenue,
                            lot_data=lot_data,
                            chart_data=chart_data)
    except Exception as e:
        flash(f'An error occurred while loading the dashboard: {str(e)}', 'danger')
        return redirect(url_for('main.index'))

@bp.route('/parking-lots', methods=['GET', 'POST'])
@login_required
@admin_required
def parking_lots():
    form = ParkingLotForm()
    if form.validate_on_submit():
        try:
            lot = ParkingLot(
                name=form.name.data,
                location=form.location.data,
                total_spots=form.total_spots.data,
                rate_per_hour=form.rate_per_hour.data,
                pincode=form.pincode.data
            )
            db.session.add(lot)
            db.session.commit()
            
            # Create parking spots with proper spot numbers
            for i in range(form.total_spots.data):
                spot = ParkingSpot(
                    lot_id=lot.id,
                    spot_number=i + 1,  # Start from 1
                    is_available=True  # Available
                )
                db.session.add(spot)
            
            db.session.commit()
            flash('Parking lot added successfully!', 'success')
            return redirect(url_for('admin.parking_lots'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding parking lot: {str(e)}', 'danger')
    
    lots = ParkingLot.query.all()
    # Calculate revenue for each lot
    lot_revenues = {}
    for lot in lots:
        revenue = db.session.query(func.coalesce(func.sum(Reservation.parking_cost), 0.0))\
            .join(ParkingSpot, Reservation.spot_id == ParkingSpot.id)\
            .filter(ParkingSpot.lot_id == lot.id, Reservation.leaving_timestamp.isnot(None)).scalar() or 0.0
        lot_revenues[lot.id] = revenue
    return render_template('admin/admin_parking_lots.html', form=form, lots=lots, lot_revenues=lot_revenues)

@bp.route('/edit-parking-lot/<int:lot_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_parking_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    form = ParkingLotForm(obj=lot)
    
    if form.validate_on_submit():
        lot.name = form.name.data
        lot.location = form.location.data
        lot.total_spots = form.total_spots.data
        lot.rate_per_hour = form.rate_per_hour.data
        db.session.commit()
        flash('Parking lot updated successfully!', 'success')
        return redirect(url_for('admin.parking_lots'))
    
    return render_template('admin/edit_parking_lot.html', form=form, lot=lot)

@bp.route('/parking_lot/<int:lot_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_parking_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    try:
        # Check if any spots are occupied
        if ParkingSpot.query.filter_by(lot_id=lot_id, is_available=False).first():
            flash('Cannot delete parking lot with occupied spots', 'danger')
            return redirect(url_for('admin.parking_lots'))
        
        # Delete all spots first
        ParkingSpot.query.filter_by(lot_id=lot_id).delete()
        db.session.delete(lot)
        db.session.commit()
        flash('Parking lot deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting parking lot: {str(e)}', 'danger')
    
    return redirect(url_for('admin.parking_lots'))

@bp.route('/users')
@login_required
@admin_required
def users():
    # Get users with their statistics
    users_with_stats = db.session.query(
        User,
        func.count(Reservation.id).label('total_bookings'),
        func.coalesce(func.sum(Reservation.parking_cost), 0.0).label('total_spent')
    ).outerjoin(
        Reservation, User.id == Reservation.user_id
    ).group_by(
        User.id
    ).all()
    
    return render_template('admin/admin_users.html', users=users_with_stats)

@bp.route('/edit_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = EditUserForm()
    
    if form.validate_on_submit():
        try:
            user.name = form.name.data
            user.email = form.email.data
            user.address = form.address.data
            user.pincode = form.pincode.data
            
            if form.password.data:
                user.set_password(form.password.data)
            
            db.session.commit()
            flash('User updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating user: {str(e)}', 'danger')
    
    return redirect(url_for('admin.users'))

@bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    try:
        # Check if user has any active reservations
        if Reservation.query.filter_by(user_id=user_id, leaving_timestamp=None).first():
            flash('Cannot delete user with active reservations', 'danger')
            return redirect(url_for('admin.users'))
        
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {str(e)}', 'danger')
    
    return redirect(url_for('admin.users'))

@bp.route('/occupied_spots')
@login_required
@admin_required
def occupied_spots():
    occupied_spots = db.session.query(
        ParkingSpot, ParkingLot, Reservation, User
    ).join(
        ParkingLot, ParkingSpot.lot_id == ParkingLot.id
    ).join(
        Reservation, ParkingSpot.id == Reservation.spot_id
    ).join(
        User, Reservation.user_id == User.id
    ).filter(
        ParkingSpot.is_available == False,
        Reservation.leaving_timestamp.is_(None)
    ).all()
    
    return render_template('admin/admin_occupied_spots.html', 
                         occupied_spots=occupied_spots,
                         now=datetime.now())

@bp.route('/end_reservation/<int:spot_id>', methods=['POST'])
@login_required
@admin_required
def end_reservation(spot_id):
    try:
        reservation = Reservation.query.filter_by(
            spot_id=spot_id,
            leaving_timestamp=None
        ).first_or_404()
        
        spot = ParkingSpot.query.get(spot_id)
        if not spot:
            flash('Parking spot not found', 'danger')
            return redirect(url_for('admin.occupied_spots'))
        
        # Calculate parking cost
        duration = datetime.now() - reservation.entry_timestamp
        hours = math.ceil(duration.total_seconds() / 3600)
        cost = hours * spot.lot.rate_per_hour
        
        # Update reservation
        reservation.leaving_timestamp = datetime.now()
        reservation.parking_cost = cost
        
        # Update spot status
        spot.is_available = True
        
        db.session.commit()
        flash('Reservation ended successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error ending reservation: {str(e)}', 'danger')
    
    return redirect(url_for('admin.occupied_spots'))

@bp.route('/force_release/<int:reservation_id>', methods=['POST'])
@login_required
@admin_required
def force_release(reservation_id):
    try:
        reservation = Reservation.query.get_or_404(reservation_id)
        spot = ParkingSpot.query.get(reservation.spot_id)
        
        if not spot:
            flash('Parking spot not found', 'danger')
            return redirect(url_for('admin.occupied_spots'))
        
        # Calculate parking cost
        duration = datetime.now() - reservation.entry_timestamp
        hours = math.ceil(duration.total_seconds() / 3600)
        cost = hours * spot.lot.rate_per_hour
        
        # Update reservation
        reservation.leaving_timestamp = datetime.now()
        reservation.parking_cost = cost
        
        # Update spot status
        spot.is_available = True
        
        db.session.commit()
        flash('Spot force released successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error force releasing spot: {str(e)}', 'danger')
    
    return redirect(url_for('admin.occupied_spots')) 