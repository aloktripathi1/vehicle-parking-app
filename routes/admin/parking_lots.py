from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from ..admin import admin_bp
from models import db, ParkingLot, ParkingSpot
from forms import ParkingLotForm
from sqlalchemy import func, case
import traceback

@admin_bp.route('/parking_lots', methods=['GET', 'POST'])
@login_required
def admin_parking_lots():
    if session.get('user_type') != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    form = ParkingLotForm()
    if form.validate_on_submit():
        lot = ParkingLot(
            prime_location_name=form.prime_location_name.data,
            address=form.address.data,
            pincode=form.pincode.data,
            max_spots=form.max_spots.data,
            price=form.price.data
        )
        db.session.add(lot)
        db.session.commit()
            
        for i in range(lot.max_spots):
            spot = ParkingSpot(
                lot_id=lot.id,
                status='A'
            )
            db.session.add(spot)
            
        db.session.commit()
        flash('Parking lot added successfully!', 'success')
        return redirect(url_for('admin.admin_parking_lots'))
            
    parking_lots_query = db.session.query(
        ParkingLot, func.count(ParkingSpot.id).label('total_spots'),
        func.sum(case((ParkingSpot.status == 'O', 1), else_=0)).label('occupied_spots')
    ).outerjoin(
        ParkingSpot, ParkingLot.id == ParkingSpot.lot_id
    ).group_by(
        ParkingLot.id
    ).all()
    parking_lots = [lot for lot, _, _ in parking_lots_query]
    lot_revenues = {}
    for lot in parking_lots:
        revenue = db.session.query(func.sum(ParkingSpot.reservations.property.mapper.class_.parking_cost)).join(ParkingSpot).filter(ParkingSpot.lot_id == lot.id).scalar() or 0
        lot_revenues[lot.id] = revenue
    return render_template('admin/admin_parking_lots.html', form=form, parking_lots=parking_lots, lot_revenues=lot_revenues) 