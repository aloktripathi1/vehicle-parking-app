import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, ParkingLot, ParkingSpot, Reservation
from forms import LoginForm, RegisterForm, ParkingLotForm, EditUserForm
from flask_migrate import Migrate
import sqlite3
import json
import math
from sqlalchemy import func, inspect
from sqlalchemy import or_
import traceback
from utils import format_ist_datetime, utc_to_ist

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'I am Alok Tripathi and this is my secret key!')

try:
    os.makedirs(app.instance_path)
except OSError:
    pass

db_path = os.path.join(app.instance_path, 'database.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True 

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main.login'


app.jinja_env.globals.update(
    format_ist_datetime=format_ist_datetime,
    utc_to_ist=utc_to_ist
)

from routes.main import main_bp
from routes.admin import admin_bp
from routes.user import user_bp

app.register_blueprint(main_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(user_bp, url_prefix='/user')

def create_default_admin():
    """Create default admin user if not exists"""
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@parkease.com')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
    admin_name = os.environ.get('ADMIN_NAME', 'Admin User')
    
    admin = User.query.filter_by(email=admin_email, role='admin').first()
    if not admin:
        admin = User(
            email=admin_email,
            name=admin_name,
            role='admin',
            address='',
            pincode=''
        )
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
        print(f"Default admin created: {admin_email}")
    else:
        print(f"Admin already exists: {admin_email}")

with app.app_context():
    db.create_all()
    create_default_admin()

# -------------------- Error Handling --------------------

@app.errorhandler(500)
def internal_error(error):
    app.logger.error('Server Error: %s', (traceback.format_exc()))
    return render_template('main/error.html', error=str(error), traceback=traceback.format_exc()), 500

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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

def verify_spot_statuses(lot_id):
    try:
        spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
        
        active_reservations = Reservation.query.filter(
            Reservation.spot_id.in_([spot.id for spot in spots]),
            Reservation.leaving_timestamp.is_(None)).all()
        
        occupied_spot_ids = {res.spot_id for res in active_reservations}
        
        for spot in spots:
            should_be_occupied = spot.id in occupied_spot_ids
            if should_be_occupied and spot.status != 'O':
                app.logger.warning(f"Fixing spot {spot.id} status from {spot.status} to O")
                spot.status = 'O'
            elif not should_be_occupied and spot.status != 'A':
                app.logger.warning(f"Fixing spot {spot.id} status from {spot.status} to A")
                spot.status = 'A'
        
        db.session.commit()
        return True
    except Exception as e:
        app.logger.error(f"Error verifying spot statuses: {str(e)}")
        db.session.rollback()
        return False

if __name__ == '__main__':
    app.run(debug=True)
    