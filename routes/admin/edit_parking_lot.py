from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from ..admin import admin_bp
from models import db, ParkingLot, ParkingSpot
from forms import ParkingLotForm

@admin_bp.route('/parking_lot/<int:lot_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_parking_lot(lot_id):
    if session.get('user_type') != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    lot = ParkingLot.query.get_or_404(lot_id)
    form = ParkingLotForm(obj=lot)
    
    if form.validate_on_submit():
        try:
            old_max_spots = lot.max_spots
            new_max_spots = form.max_spots.data
            
            lot.prime_location_name = form.prime_location_name.data
            lot.address = form.address.data
            lot.pincode = form.pincode.data
            lot.price = form.price.data
            
            if new_max_spots > old_max_spots:
                for i in range(old_max_spots, new_max_spots):
                    spot = ParkingSpot(
                        lot_id=lot.id,
                        status='A'
                    )
                    db.session.add(spot)
            
            lot.max_spots = new_max_spots
            db.session.commit()
            flash('Parking lot updated successfully!', 'success')
            return redirect(url_for('admin.admin_parking_lots'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the parking lot', 'danger')
    
    return render_template('admin/edit_parking_lot.html', form=form, parking_lot=lot) 