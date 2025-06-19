from datetime import datetime
from flask import render_template, redirect, url_for, flash, session
from flask_login import login_required, current_user
from ..user import user_bp
from models import db, Reservation, ParkingSpot, ParkingLot

@user_bp.route('/dashboard')
@login_required
def user_dashboard():
    try:
        if session.get('user_type') != 'user':
            flash('Access denied', 'danger')
            return redirect(url_for('main.index'))
        
        active_reservation = db.session.query(
            Reservation, ParkingSpot, ParkingLot
        ).join(
            ParkingSpot, Reservation.spot_id == ParkingSpot.id
        ).join(
            ParkingLot, ParkingSpot.lot_id == ParkingLot.id
        ).filter(
            Reservation.user_id == current_user.id,
            Reservation.leaving_timestamp.is_(None)
        ).first()
        
        profile_complete = bool(current_user.address and current_user.pincode)
        
        reservation_history = db.session.query(
            Reservation, ParkingSpot, ParkingLot
        ).join(
            ParkingSpot, Reservation.spot_id == ParkingSpot.id
        ).join(
            ParkingLot, ParkingSpot.lot_id == ParkingLot.id
        ).filter(
            Reservation.user_id == current_user.id,
            Reservation.leaving_timestamp.isnot(None)
        ).order_by(Reservation.leaving_timestamp.desc()).all()
        
        filtered_reservation_history = []
        for r in reservation_history:
            if r[1] is None or r[2] is None:
                print(f"Skipping reservation with missing spot or lot: {r}")
                continue
            filtered_reservation_history.append(r)
        reservation_history = filtered_reservation_history
        
        total_spent = round(sum(r[0].parking_cost or 0 for r in reservation_history), 2)

        total_time_spent = 0
        for reservation in reservation_history:
            if reservation[0].parking_timestamp and reservation[0].leaving_timestamp:
                duration = reservation[0].leaving_timestamp - reservation[0].parking_timestamp
                total_time_spent += duration.total_seconds()
        
        hours = int(total_time_spent // 3600)
        minutes = int((total_time_spent % 3600) // 60)
        if hours > 0:
            total_time_spent = f"{hours}h {minutes}m"
        else:
            total_time_spent = f"{minutes}m"
        
        now = datetime.utcnow()
        
        chart_data = {
            'labels': [f"{r[2].prime_location_name} ({r[0].parking_timestamp.strftime('%d/%m/%Y')})" for r in reservation_history[-5:]],
            'costs': [float(r[0].parking_cost or 0) for r in reservation_history[-5:]]
        }
        
        return render_template('user_dashboard.html',
            active_reservation=active_reservation,
            profile_complete=profile_complete,
            reservation_history=reservation_history,
            total_spent=total_spent,
            total_time_spent=total_time_spent,
            chart_data=chart_data,
            now=now)
    except Exception as e:
        import traceback
        print('User dashboard error:', e)
        traceback.print_exc()
        flash('An error occurred while loading the dashboard', 'danger')
        return redirect(url_for('main.index')) 