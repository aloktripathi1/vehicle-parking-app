from flask import render_template, request, session, redirect, url_for, flash
from flask_login import login_required
from ..admin import admin_bp
from models import db, Reservation, ParkingSpot, ParkingLot, User
from datetime import datetime
from sqlalchemy import and_

@admin_bp.route('/parking_history', methods=['GET'])
@login_required
def parking_history():
    if session.get('user_type') != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))

    lot_id = request.args.get('lot_id', type=int)
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    month = request.args.get('month')
    year = request.args.get('year', type=int)

    query = db.session.query(Reservation, ParkingSpot, ParkingLot, User)
    query = query.join(ParkingSpot, Reservation.spot_id == ParkingSpot.id)
    query = query.join(ParkingLot, ParkingSpot.lot_id == ParkingLot.id)
    query = query.outerjoin(User, Reservation.user_id == User.id)

    if lot_id:
        query = query.filter(ParkingLot.id == lot_id)
    if date_from:
        date_from_dt = datetime.strptime(date_from, '%Y-%m-%d')
        query = query.filter(Reservation.parking_timestamp >= date_from_dt)
    if date_to:
        date_to_dt = datetime.strptime(date_to, '%Y-%m-%d')
        query = query.filter(Reservation.parking_timestamp <= date_to_dt)
    if month and year:
        month = int(month)
        year = int(year)
        query = query.filter(db.extract('month', Reservation.parking_timestamp) == month)
        query = query.filter(db.extract('year', Reservation.parking_timestamp) == year)
    reservations = query.order_by(Reservation.parking_timestamp.desc()).all()
    lots = ParkingLot.query.order_by(ParkingLot.prime_location_name).all()

    return render_template('admin/admin_parking_history.html',
        reservations=reservations,
        lots=lots,
        selected_lot=lot_id,
        date_from=date_from,
        date_to=date_to,
        month=month,
        year=year
    ) 