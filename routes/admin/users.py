from flask import render_template, redirect, url_for, flash, session
from flask_login import login_required, current_user
from ..admin import admin_bp
from models import db, User, Reservation, ParkingSpot, ParkingLot
from sqlalchemy import func

@admin_bp.route('/users')
@login_required
def admin_users():
    if session.get('user_type') != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    users_query = db.session.query(
        User,
        func.count(Reservation.id).label('total_reservations'),
        func.sum(Reservation.parking_cost).label('total_spent')
    ).outerjoin(
        Reservation, User.id == Reservation.user_id
    ).group_by(
        User.id
    ).all()
    users = []
    for user, total_reservations, total_spent in users_query:
        user.total_bookings = total_reservations
        user.total_spent = total_spent or 0
        users.append(user)
        
    active_bookings = {}
    for user in users:
        active_booking = db.session.query(
            Reservation, ParkingSpot, ParkingLot
        ).join(
            ParkingSpot, Reservation.spot_id == ParkingSpot.id
        ).join(
            ParkingLot, ParkingSpot.lot_id == ParkingLot.id
        ).filter(
            Reservation.user_id == user.id,
            Reservation.leaving_timestamp.is_(None)
        ).first()
        active_bookings[user.id] = active_booking
        
    return render_template('admin/admin_users.html',
        users=users,
        active_bookings=active_bookings)
            
@admin_bp.route('/user/<int:user_id>/reservations')
@login_required
def admin_user_reservation_history(user_id):
    if session.get('user_type') != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    user = User.query.get_or_404(user_id)
    reservations = db.session.query(
        Reservation, ParkingSpot, ParkingLot
    ).join(
        ParkingSpot, Reservation.spot_id == ParkingSpot.id
    ).join(
        ParkingLot, ParkingSpot.lot_id == ParkingLot.id
    ).filter(
        Reservation.user_id == user_id
    ).order_by(
        Reservation.parking_timestamp.desc()
    ).all()
    return render_template('admin/admin_user_reservations.html', user=user, reservations=reservations)
