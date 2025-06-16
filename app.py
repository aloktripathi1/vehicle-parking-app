import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Admin, ParkingLot, ParkingSpot, Reservation
from forms import LoginForm, RegisterForm, ParkingLotForm, EditUserForm
from flask_migrate import Migrate
import sqlite3
import json
import math
from sqlalchemy import func, inspect
from sqlalchemy import or_
import traceback

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-please-change-in-production')

# Ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

# Configure SQLite database to use a file in the instance folder
db_path = os.path.join(app.instance_path, 'database.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True  # Enable debug mode

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize database
with app.app_context():
    # Create tables if they don't exist
    db.create_all()
    
    # Create admin user if it doesn't exist
    admin = Admin.query.filter_by(username='admin').first()
    if not admin:
        admin = Admin(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

@app.errorhandler(500)
def internal_error(error):
    app.logger.error('Server Error: %s', (traceback.format_exc()))
    return render_template('error.html', error=str(error), traceback=traceback.format_exc()), 500

@login_manager.user_loader
def load_user(user_id):
    if session.get('user_type') == 'admin':
        return Admin.query.get(int(user_id))
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if session.get('user_type') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('user_dashboard'))
        
    form = LoginForm()
    if form.validate_on_submit():
        # Check for admin first
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin and admin.check_password(form.password.data):
            login_user(admin, remember=form.remember.data)
            session['user_type'] = 'admin'
            session['user_id'] = admin.id
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        
        # Then check for regular user
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            session['user_type'] = 'user'
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('user_dashboard'))
        
        flash('Invalid username or password', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists', 'danger')
            return render_template('register.html', form=form)
        
        try:
            user = User(
                username=form.username.data,
                email=form.email.data,
                name=form.name.data,
                address='',  # Initialize with empty string
                pincode=''   # Initialize with empty string
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            
            # Automatically log in the user
            login_user(user)
            session['user_type'] = 'user'
            flash('Registration successful! Welcome to ParkEase.', 'success')
            return redirect(url_for('user_dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            return render_template('register.html', form=form)
            
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user_type', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if session.get('user_type') != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    try:
        parking_lots = ParkingLot.query.all()
        total_spots = ParkingSpot.query.count()
        occupied_spots = ParkingSpot.query.filter_by(status='O').count()
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
        occupied_spots_yesterday = ParkingSpot.query.filter_by(status='O').count()
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
            occupied_lot_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
            
            lot_data.append({
                'name': lot.prime_location_name,
                'revenue': lot_revenue,
                'total_spots': total_lot_spots,
                'occupied_spots': occupied_lot_spots
            })
        
        # Prepare chart data
        chart_data = {
            'lot_data': lot_data
        }
        
        return render_template('admin_dashboard.html',
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
        app.logger.error(f"Error in admin_dashboard: {str(e)}")
        flash(f'An error occurred while loading the dashboard: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/user/dashboard')
@login_required
def user_dashboard():
    try:
        if session.get('user_type') != 'user':
            flash('Access denied', 'danger')
            return redirect(url_for('index'))
        
        # Get user's active reservation if any
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
        
        # Check if profile is complete
        profile_complete = bool(current_user.address and current_user.pincode)
        
        # Get user's reservation history
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
        
        # Calculate total spent
        total_spent = round(sum(r[0].parking_cost or 0 for r in reservation_history), 2)
        
        # Calculate total time spent
        total_time_spent = 0
        for reservation in reservation_history:
            if reservation[0].parking_timestamp and reservation[0].leaving_timestamp:
                duration = reservation[0].leaving_timestamp - reservation[0].parking_timestamp
                total_time_spent += duration.total_seconds()
        
        # Format total time spent
        hours = int(total_time_spent // 3600)
        minutes = int((total_time_spent % 3600) // 60)
        if hours > 0:
            total_time_spent = f"{hours}h {minutes}m"
        else:
            total_time_spent = f"{minutes}m"
        
        # Get current time in UTC for duration calculations
        now = datetime.utcnow()
        
        # Chart data for history
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
        flash('An error occurred while loading the dashboard', 'danger')
        return redirect(url_for('index'))

@app.route('/user/parking_lots')
@login_required
def user_parking_lots():
    try:
        if session.get('user_type') != 'user':
            flash('Access denied', 'danger')
            return redirect(url_for('index'))
            
        # Get all parking lots
        parking_lots = ParkingLot.query.all()
        
        # Get available spots for each lot
        available_spots = {}
        available_spot_ids = {}
        for lot in parking_lots:
            # Get all spots for this lot
            spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()
            
            # Count available spots (status = 'A')
            available_count = sum(1 for spot in spots if spot.status == 'A')
            available_spots[lot.id] = available_count
            
            # Get IDs of available spots
            available_spot_ids[lot.id] = [spot.id for spot in spots if spot.status == 'A']
        
        return render_template('user_parking_lots.html',
                             parking_lots=parking_lots,
                             available_spots=available_spots,
                             available_spot_ids=available_spot_ids,
                             current_user=current_user)
    except Exception as e:
        app.logger.error(f"Error loading parking lots: {str(e)}\n{traceback.format_exc()}")
        flash('An error occurred while loading parking lots. Please try again later.', 'error')
        return redirect(url_for('user_dashboard'))

def has_active_booking(user_id):
    """Check if user has any active bookings"""
    try:
        active_statuses = ['active', 'booked', 'in-progress']
        active_booking = Reservation.query.filter(
            Reservation.user_id == user_id,
            Reservation.status.in_(active_statuses)
        ).first()
        return active_booking is not None
    except Exception as e:
        print(f"Error checking active bookings: {e}")
        return False

@app.route('/book_spot', methods=['POST'])
@login_required
def book_spot():
    try:
        if session.get('user_type') != 'user':
            return jsonify({
                'success': False,
                'message': 'Access denied'
            })
        
        # Get form data first to fail fast if missing
        lot_id = request.form.get('lot_id')
        vehicle_number = request.form.get('vehicle_number')
        
        if not lot_id or not vehicle_number:
            return jsonify({
                'success': False,
                'message': 'Please provide all required information.'
            })
        
        # Check profile completion and active bookings in parallel
        profile_complete = bool(current_user.address and current_user.pincode)
        active_reservation = Reservation.query.filter_by(
            user_id=current_user.id,
            leaving_timestamp=None
        ).first()
        
        if not profile_complete:
            return jsonify({
                'success': False,
                'message': 'Please complete your profile before booking a spot.'
            })
        
        if active_reservation:
            return jsonify({
                'success': False,
                'message': 'You already have an active booking.'
            })
        
        # Get parking lot and spot in a single query
        parking_lot = ParkingLot.query.get(lot_id)
        if not parking_lot:
            return jsonify({
                'success': False,
                'message': 'Invalid parking lot selected.'
            })
        
        spot = ParkingSpot.query.filter_by(
            lot_id=lot_id,
            status='A'
        ).first()
        
        if not spot:
            return jsonify({
                'success': False,
                'message': 'No available spots in this parking lot.'
            })
        
        # Create reservation and update spot in a single transaction
        try:
            reservation = Reservation(
                user_id=current_user.id,
                spot_id=spot.id,
                vehicle_number=vehicle_number,
                parking_timestamp=datetime.utcnow()
            )
            spot.status = 'O'  # Occupied
            
            db.session.add(reservation)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Booking successful!'
            })
            
        except Exception as e:
            db.session.rollback()
            raise e
        
    except Exception as e:
        app.logger.error(f"Error creating booking: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while creating the booking.'
        })

@app.route('/user/vacate_spot/<int:reservation_id>', methods=['POST'])
@login_required
def vacate_spot(reservation_id):
    if session.get('user_type') != 'user':
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    reservation = Reservation.query.get_or_404(reservation_id)
    
    # Ensure the reservation belongs to the current user
    if reservation.user_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('user_dashboard'))
    
    # Ensure the reservation is active
    if reservation.leaving_timestamp is not None:
        flash('This reservation is already completed', 'warning')
        return redirect(url_for('user_dashboard'))
    
    # Get the spot and update its status
    spot = ParkingSpot.query.get(reservation.spot_id)
    spot.status = 'A'  # Available
    
    # Update reservation
    leaving_time = datetime.now()
    reservation.leaving_timestamp = leaving_time
    
    # Calculate parking duration in minutes
    parking_time = reservation.parking_timestamp
    duration_minutes = (leaving_time - parking_time).total_seconds() / 60
    
    # Get parking lot price
    parking_lot = ParkingLot.query.get(spot.lot_id)
    
    # Calculate cost based on minutes
    reservation.parking_cost = round((duration_minutes / 60) * parking_lot.price, 2)
    
    # Update payment details
    payment_method = request.form.get('payment_method')
    if payment_method:
        reservation.payment_status = 'Paid'
        reservation.payment_mode = payment_method
        reservation.payment_time = leaving_time
    
    db.session.commit()
    
    # Format duration for flash message
    if duration_minutes < 60:
        duration_text = f"{int(duration_minutes)} minutes"
    else:
        hours = int(duration_minutes // 60)
        minutes = int(duration_minutes % 60)
        duration_text = f"{hours} hour{'s' if hours != 1 else ''}"
        if minutes > 0:
            duration_text += f", {minutes} minute{'s' if minutes != 1 else ''}"
    
    flash(f'Spot vacated successfully. Duration: {duration_text}. Payment of ₹{reservation.parking_cost:.2f} completed via {payment_method}.', 'success')
    return redirect(url_for('user_dashboard'))

@app.route('/admin/parking_lots', methods=['GET', 'POST'])
@login_required
def admin_parking_lots():
    if session.get('user_type') != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    form = ParkingLotForm()
    if form.validate_on_submit():
        parking_lot = ParkingLot(
            prime_location_name=form.prime_location_name.data,
            price=form.price.data,
            address=form.address.data,
            pincode=form.pincode.data,
            max_spots=form.max_spots.data
        )
        db.session.add(parking_lot)
        db.session.commit()
        
        # Auto-generate parking spots
        for i in range(1, parking_lot.max_spots + 1):
            spot = ParkingSpot(
                lot_id=parking_lot.id,
                status='A'  # Available
            )
            db.session.add(spot)
        
        db.session.commit()
        flash('Parking lot added successfully', 'success')
        return redirect(url_for('admin_parking_lots'))
    
    parking_lots = ParkingLot.query.all()
    lot_revenues = {}
    for lot in parking_lots:
        lot_revenue = db.session.query(func.sum(Reservation.parking_cost))\
            .join(ParkingSpot, Reservation.spot_id == ParkingSpot.id)\
            .filter(ParkingSpot.lot_id == lot.id, Reservation.leaving_timestamp.isnot(None)).scalar() or 0.0
        lot_revenues[lot.id] = lot_revenue
    return render_template('admin_parking_lots.html', form=form, parking_lots=parking_lots, lot_revenues=lot_revenues)

@app.route('/admin/parking_lot/<int:lot_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_parking_lot(lot_id):
    if session.get('user_type') != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    parking_lot = ParkingLot.query.get_or_404(lot_id)
    
    if request.method == 'POST':
        # Update parking lot details
        parking_lot.prime_location_name = request.form.get('prime_location_name')
        parking_lot.price = float(request.form.get('price'))
        parking_lot.address = request.form.get('address')
        parking_lot.pincode = request.form.get('pincode')
        
        # Handle max_spots changes
        new_max_spots = int(request.form.get('max_spots'))
        if new_max_spots > parking_lot.max_spots:
            # Add new spots
            for i in range(parking_lot.max_spots + 1, new_max_spots + 1):
                spot = ParkingSpot(
                    lot_id=parking_lot.id,
                    status='A'  # Available
                )
                db.session.add(spot)
        
        parking_lot.max_spots = new_max_spots
        db.session.commit()
        
        flash('Parking lot updated successfully', 'success')
        return redirect(url_for('admin_parking_lots'))
    
    return redirect(url_for('admin_parking_lots'))

@app.route('/admin/parking_lot/<int:lot_id>/delete', methods=['POST'])
@login_required
def delete_parking_lot(lot_id):
    if session.get('user_type') != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    parking_lot = ParkingLot.query.get_or_404(lot_id)
    
    # Check if any spots are occupied
    occupied_spots = ParkingSpot.query.filter_by(lot_id=lot_id, status='O').count()
    if occupied_spots > 0:
        flash('Cannot delete parking lot with occupied spots', 'danger')
        return redirect(url_for('admin_parking_lots'))
    
    # Delete all spots first
    ParkingSpot.query.filter_by(lot_id=lot_id).delete()
    
    # Delete the parking lot
    db.session.delete(parking_lot)
    db.session.commit()
    
    flash('Parking lot deleted successfully', 'success')
    return redirect(url_for('admin_parking_lots'))

@app.route('/admin/users')
@login_required
def admin_users():
    if session.get('user_type') != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    try:
        # Get sort parameters from URL
        sort_column = request.args.get('sort', 'signup_date')
        sort_direction = request.args.get('direction', 'desc')
        
        # Validate sort column
        valid_columns = {
            'signup_date': User.created_at,
            'total_bookings': func.count(Reservation.id),
            'total_spent': func.coalesce(func.sum(Reservation.parking_cost), 0.0)
        }
        
        if sort_column not in valid_columns:
            sort_column = 'signup_date'
        
        # Build the query
        query = db.session.query(
            User,
            func.count(Reservation.id).label('total_bookings'),
            func.coalesce(func.sum(Reservation.parking_cost), 0.0).label('total_spent')
        ).outerjoin(
            Reservation, User.id == Reservation.user_id
        ).group_by(
            User.id
        )
        
        # Apply sorting
        sort_column_expr = valid_columns[sort_column]
        if sort_direction == 'asc':
            query = query.order_by(sort_column_expr.asc())
        else:
            query = query.order_by(sort_column_expr.desc())
        
        # Execute query
        results = query.all()
        
        # Convert the query results to a list of user objects with additional attributes
        users_with_stats = []
        for user, total_bookings, total_spent in results:
            user.total_bookings = total_bookings or 0
            user.total_spent = total_spent or 0.0
            users_with_stats.append(user)
        
        form = EditUserForm()
        return render_template('admin_users.html', users=users_with_stats, form=form)
    except Exception as e:
        app.logger.error(f"Error in admin users: {str(e)}")
        flash('An error occurred while loading users. Please try again.', 'danger')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/occupied_spots')
@login_required
def admin_occupied_spots():
    if session.get('user_type') != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    try:
        # Get current time in UTC for duration calculation
        now = datetime.utcnow()
        
        # Get all occupied spots with their reservation details
        occupied_spots = db.session.query(
            ParkingSpot, ParkingLot, Reservation, User
        ).join(
            ParkingLot, ParkingSpot.lot_id == ParkingLot.id
        ).join(
            Reservation, ParkingSpot.id == Reservation.spot_id
        ).join(
            User, Reservation.user_id == User.id
        ).filter(
            ParkingSpot.status == 'O',
            Reservation.leaving_timestamp.is_(None)
        ).all() or []
        
        return render_template('admin_occupied_spots.html', occupied_spots=occupied_spots, now=now)
    except Exception as e:
        app.logger.error(f"Error in admin occupied spots: {str(e)}")
        flash('An error occurred while loading occupied spots. Please try again.', 'danger')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/end_reservation/<int:spot_id>', methods=['POST'])
@login_required
def end_reservation(spot_id):
    if session.get('user_type') != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    # Get the spot and its current reservation
    spot = ParkingSpot.query.get_or_404(spot_id)
    reservation = Reservation.query.filter_by(spot_id=spot_id, leaving_timestamp=None).first()
    
    if not reservation:
        flash('No active reservation found for this spot', 'warning')
        return redirect(url_for('admin_occupied_spots'))
    
    # Get the parking lot for price calculation
    lot = ParkingLot.query.get(spot.lot_id)
    
    # Calculate the duration and cost
    now = datetime.now()
    duration_hours = (now - reservation.parking_timestamp).total_seconds() / 3600
    cost = round(duration_hours * lot.price, 2)
    
    # Update the reservation
    reservation.leaving_timestamp = now
    reservation.parking_cost = cost
    
    # Update the spot status
    spot.status = 'A'  # Available
    
    db.session.commit()
    
    flash(f'Reservation ended successfully. Total cost: ₹{cost:.2f}', 'success')
    return redirect(url_for('admin_occupied_spots'))

@app.route('/api/parking_stats')
def api_parking_stats():
    parking_lots = ParkingLot.query.count()
    total_spots = ParkingSpot.query.count()
    occupied_spots = ParkingSpot.query.filter_by(status='O').count()
    available_spots = total_spots - occupied_spots
    
    return jsonify({
        'parking_lots': parking_lots,
        'total_spots': total_spots,
        'occupied_spots': occupied_spots,
        'available_spots': available_spots
    })

@app.route('/api/user/<int:user_id>/reservations')
@login_required
def api_user_reservations(user_id):
    if current_user.id != user_id and session.get('user_type') != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    reservations = db.session.query(
        Reservation.id,
        Reservation.parking_timestamp,
        Reservation.leaving_timestamp,
        Reservation.parking_cost,
        ParkingLot.prime_location_name
    ).join(
        ParkingSpot, Reservation.spot_id == ParkingSpot.id
    ).join(
        ParkingLot, ParkingSpot.lot_id == ParkingLot.id
    ).filter(
        Reservation.user_id == user_id,
        Reservation.leaving_timestamp.isnot(None)
    ).all()
    
    result = []
    for r in reservations:
        result.append({
            'id': r[0],
            'parking_timestamp': r[1].isoformat() if r[1] else None,
            'leaving_timestamp': r[2].isoformat() if r[2] else None,
            'parking_cost': float(r[3]) if r[3] else None,
            'location': r[4]
        })
    
    return jsonify(result)

@app.route('/admin/edit_user/<int:user_id>', methods=['POST'])
@login_required
def edit_user(user_id):
    if session.get('user_type') != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    form = EditUserForm()
    
    if form.validate_on_submit():
        user.name = form.full_name.data
        user.email = form.email.data
        user.address = form.address.data
        user.pincode = form.pincode.data
        db.session.commit()
        flash('User details updated successfully.', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')
    
    return redirect(url_for('admin_users'))

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if session.get('user_type') != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    
    # Delete all reservations associated with this user
    Reservation.query.filter_by(user_id=user_id).delete()
    
    # Now delete the user
    db.session.delete(user)
    db.session.commit()
    
    flash('User and their reservations deleted successfully.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/search_lots', methods=['POST'])
@login_required
def search_lots():
    if session.get('user_type') != 'user':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json() if request.is_json else request.form
    query = data.get('search_query', '').strip()
    if not query:
        return jsonify({'results': []})
    lots = ParkingLot.query.filter(
        (ParkingLot.address.ilike(f'%{query}%')) |
        (ParkingLot.pincode.ilike(f'%{query}%'))
    ).all()
    results = []
    for lot in lots:
        available_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').count()
        results.append({
            'id': lot.id,
            'address': lot.address,
            'available_spots': available_spots
        })
    return jsonify({'results': results})

@app.route('/admin/force_release/<int:reservation_id>', methods=['POST'])
@login_required
def force_release(reservation_id):
    if session.get('user_type') != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('admin_occupied_spots'))
    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation.leaving_timestamp is not None:
        flash('This reservation is already completed.', 'warning')
        return redirect(url_for('admin_occupied_spots'))
    # Set leaving_timestamp to now
    now = datetime.now()
    reservation.leaving_timestamp = now
    # Free up the spot
    spot = ParkingSpot.query.get(reservation.spot_id)
    spot.status = 'A'
    # Mark as force released (add column if not present)
    if hasattr(reservation, 'force_released'):
        reservation.force_released = True
    db.session.commit()
    flash(f'Spot {spot.id} force released. Booking ended.', 'success')
    return redirect(url_for('admin_occupied_spots'))

@app.route('/user/edit_profile', methods=['POST'])
@login_required
def edit_profile():
    try:
        if session.get('user_type') != 'user':
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': False,
                    'message': 'Access denied'
                })
            flash('Access denied', 'danger')
            return redirect(url_for('index'))
        
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
                    'message': 'Please fill in all required fields.'
                })
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('user_dashboard'))
        
        # Check if email is already taken by another user
        existing_user = User.query.filter(User.email == email, User.id != current_user.id).first()
        if existing_user:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': False,
                    'message': 'Email is already taken by another user.'
                })
            flash('Email is already taken by another user.', 'danger')
            return redirect(url_for('user_dashboard'))
        
        # Update user profile
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
        
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('user_dashboard'))
        
    except Exception as e:
        app.logger.error(f"Error updating profile: {str(e)}\n{traceback.format_exc()}")
        db.session.rollback()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False,
                'message': 'An error occurred while updating your profile.'
            })
        
        flash('An error occurred while updating your profile.', 'danger')
        return redirect(url_for('user_dashboard'))

@app.route('/api/users/search')
@login_required
def search_users():
    if session.get('user_type') != 'admin':
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    # Get search parameters
    query = request.args.get('q', '').strip()
    sort_column = request.args.get('sort', 'signup_date')
    sort_direction = request.args.get('direction', 'desc')
    
    if not query:
        return jsonify({'success': False, 'error': 'Search query is required'}), 400
    
    # Validate sort column
    valid_columns = {
        'signup_date': User.created_at,
        'total_bookings': func.count(Reservation.id),
        'total_spent': func.sum(Reservation.parking_cost)
    }
    
    if sort_column not in valid_columns:
        sort_column = 'signup_date'
    
    try:
        # Build the search query
        search_query = db.session.query(
            User,
            func.count(Reservation.id).label('total_bookings'),
            func.sum(Reservation.parking_cost).label('total_spent')
        ).outerjoin(
            Reservation, User.id == Reservation.user_id
        ).group_by(
            User.id
        ).filter(
            or_(
                User.name.ilike(f'%{query}%'),
                User.email.ilike(f'%{query}%')
            )
        )
        
        # Apply sorting
        sort_column_expr = valid_columns[sort_column]
        if sort_direction == 'asc':
            search_query = search_query.order_by(sort_column_expr.asc())
        else:
            search_query = search_query.order_by(sort_column_expr.desc())
        
        # Execute query
        results = search_query.all()
        
        # Format results
        users = []
        for user, total_bookings, total_spent in results:
            users.append({
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M'),
                'total_bookings': total_bookings or 0,
                'total_spent': float(total_spent or 0.0)
            })
        
        return jsonify({
            'success': True,
            'users': users
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/check-active-booking')
@login_required
def check_active_booking():
    """Check if the current user has any active bookings"""
    try:
        has_active = has_active_booking(current_user.id)
        return jsonify({
            'success': True,
            'hasActiveBooking': has_active
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/book-parking', methods=['POST'])
@login_required
def book_parking():
    try:
        data = request.get_json()
        parking_lot_id = data.get('parking_lot_id')
        start_time = datetime.fromisoformat(data.get('start_time'))
        end_time = datetime.fromisoformat(data.get('end_time'))
        
        # Check for active bookings
        if has_active_booking(current_user.id):
            return jsonify({
                'success': False,
                'message': 'You already have an active parking spot booked. Please cancel or complete it before booking a new one.'
            }), 400
        
        # Get parking lot
        parking_lot = ParkingLot.query.get_or_404(parking_lot_id)
        
        # Check if parking lot is full
        if parking_lot.available_spots <= 0:
            return jsonify({
                'success': False,
                'message': 'Sorry, this parking lot is full.'
            }), 400
            
        # Create booking
        booking = Reservation(
            user_id=current_user.id,
            spot_id=parking_lot.spots[0].id,  # Assuming the first spot is available
            vehicle_number='',  # Assuming no vehicle number is provided in the new booking
            parking_timestamp=start_time,
            status='booked'
        )
        
        # Update parking lot availability
        parking_lot.available_spots -= 1
        
        db.session.add(booking)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Parking spot booked successfully!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/parking-lots')
@login_required
def api_parking_lots():
    try:
        # Get all parking lots with their spots
        parking_lots = ParkingLot.query.all()
        
        # Format the data for the frontend
        lots_data = []
        for lot in parking_lots:
            # Get available spots count
            available_spots = ParkingSpot.query.filter_by(
                lot_id=lot.id,
                status='A'
            ).count()
            
            # Get all spot IDs for this lot
            spot_ids = [spot.id for spot in lot.spots]
            
            lots_data.append({
                'id': lot.id,
                'name': lot.prime_location_name,
                'address': lot.address,
                'pincode': lot.pincode,
                'price_per_hour': lot.price,
                'available_spots': available_spots,
                'spot_ids': spot_ids
            })
        
        return jsonify(lots_data)
    except Exception as e:
        app.logger.error(f"Error in api_parking_lots: {str(e)}")
        return jsonify({'error': 'Failed to fetch parking lots'}), 500

@app.route('/api/parking_lot/<int:lot_id>/spots', methods=['GET'])
@login_required
def get_parking_lot_spots(lot_id):
    if session.get('user_type') != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Get all spots for the lot
        spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
        
        # Calculate summary
        total_spots = len(spots)
        available_spots = sum(1 for spot in spots if spot.status == 'A')
        
        # Format spot data
        spots_data = [{
            'id': spot.id,
            'status': 'Available' if spot.status == 'A' else 'Occupied'
        } for spot in spots]
        
        return jsonify({
            'summary': {
                'available_spots': available_spots,
                'total_spots': total_spots
            },
            'spots': spots_data
        })
    except Exception as e:
        app.logger.error(f"Error fetching spots: {str(e)}")
        return jsonify({'error': 'Failed to fetch spots'}), 500

@app.route('/api/admin/user/<int:user_id>/reservations')
@login_required
def admin_user_reservations(user_id):
    if session.get('user_type') != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        reservations = db.session.query(
            Reservation,
            ParkingSpot,
            ParkingLot
        ).join(
            ParkingSpot, Reservation.spot_id == ParkingSpot.id
        ).join(
            ParkingLot, ParkingSpot.lot_id == ParkingLot.id
        ).filter(
            Reservation.user_id == user_id
        ).order_by(Reservation.parking_timestamp.desc()).all()
        
        result = []
        for reservation, spot, lot in reservations:
            duration = None
            if reservation.leaving_timestamp:
                duration_seconds = (reservation.leaving_timestamp - reservation.parking_timestamp).total_seconds()
                hours = int(duration_seconds // 3600)
                minutes = int((duration_seconds % 3600) // 60)
                duration = f"{hours} hours, {minutes} minutes" if hours > 0 else f"{minutes} minutes"
            
            result.append({
                'id': reservation.id,
                'parking_lot': lot.prime_location_name,
                'spot_id': spot.id,
                'vehicle_number': reservation.vehicle_number,
                'parked_at': reservation.parking_timestamp.strftime('%Y-%m-%d %H:%M') if reservation.parking_timestamp else None,
                'left_at': reservation.leaving_timestamp.strftime('%Y-%m-%d %H:%M') if reservation.leaving_timestamp else None,
                'duration': duration,
                'cost': f"₹{reservation.parking_cost:.2f}" if reservation.parking_cost else None
            })
        
        return jsonify({'reservations': result})
    except Exception as e:
        app.logger.error(f"Error fetching user reservations: {str(e)}")
        return jsonify({'error': 'Failed to fetch reservations'}), 500

if __name__ == '__main__':
    app.run(debug=True)


    