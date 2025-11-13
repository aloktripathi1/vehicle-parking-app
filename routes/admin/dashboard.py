from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, flash, session
from flask_login import login_required, current_user
from ..admin import admin_bp
from models import db, User, ParkingLot, ParkingSpot, Reservation
from sqlalchemy import func

@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    if session.get('user_type') != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)
    first_day = today.replace(day=1)
    # Users
    users = User.query.count()
    users_yesterday = db.session.query(User).filter(func.date(User.created_at) == yesterday).count()
    user_change = users - users_yesterday
    user_change_percent = ((user_change / users_yesterday) * 100) if users_yesterday else 0

    parking_lots = ParkingLot.query.all()

    total_spots = ParkingSpot.query.count()
    occupied_spots = ParkingSpot.query.filter_by(status='O').count()
    available_spots = total_spots - occupied_spots

    spot_change = 0

    total_revenue = db.session.query(func.sum(Reservation.parking_cost)).scalar() or 0
    today_revenue = db.session.query(func.sum(Reservation.parking_cost)).filter(func.date(Reservation.leaving_timestamp) == today).scalar() or 0
    yesterday_revenue = db.session.query(func.sum(Reservation.parking_cost)).filter(func.date(Reservation.leaving_timestamp) == yesterday).scalar() or 0
    revenue_change = today_revenue - yesterday_revenue
    revenue_change_percent = ((revenue_change / yesterday_revenue) * 100) if yesterday_revenue else 0

    revenue_by_lot = db.session.query(
        ParkingLot.prime_location_name,
        func.sum(Reservation.parking_cost)
    ).join(
        ParkingSpot, ParkingLot.id == ParkingSpot.lot_id
    ).join(
        Reservation, ParkingSpot.id == Reservation.spot_id
    ).group_by(
        ParkingLot.id
    ).all()

    lot_data = []
    for lot in parking_lots:
        lot_spots = ParkingSpot.query.filter_by(lot_id=lot.id).count()
        lot_occupied = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
        lot_revenue = db.session.query(func.sum(Reservation.parking_cost)).join(ParkingSpot).filter(ParkingSpot.lot_id == lot.id).scalar() or 0
        lot_data.append({
            'id': lot.id,
            'name': lot.prime_location_name,
            'total_spots': lot_spots,
            'occupied_spots': lot_occupied,
            'revenue': lot_revenue
        })
    chart_data = lot_data 
    return render_template('admin/admin_dashboard.html',
        total_revenue=round(total_revenue, 2),
        revenue_change=round(revenue_change, 2),
        revenue_change_percent=round(revenue_change_percent, 1),
        parking_lots=parking_lots,
        available_spots=available_spots,
        spot_change=spot_change,
        occupied_spots=occupied_spots,
        users=users,
        user_change=user_change,
        user_change_percent=round(user_change_percent, 1),
        lot_data=lot_data,
        chart_data=chart_data
    )
            
