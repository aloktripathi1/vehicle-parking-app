from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_type = db.Column(db.String(20), default='user')
    
    reservations = db.relationship('Reservation', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        print(f"Password hash generated for user {self.email}")
    
    def check_password(self, password):
        result = check_password_hash(self.password_hash, password)
        print(f"Password check for user {self.email}: {'success' if result else 'failed'}")
        return result
    
    def __repr__(self):
        return f'<User {self.email}>'

class Admin(UserMixin, db.Model):
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_type = db.Column(db.String(20), default='admin')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        print(f"Password hash generated for admin {self.email}")
    
    def check_password(self, password):
        result = check_password_hash(self.password_hash, password)
        print(f"Password check for admin {self.email}: {'success' if result else 'failed'}")
        return result
    
    def __repr__(self):
        return f'<Admin {self.email}>'

class ParkingLot(db.Model):
    __tablename__ = 'parking_lots'
    
    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)  # Price per hour
    address = db.Column(db.String(200), nullable=False)
    pincode = db.Column(db.Integer, nullable=False)
    max_spots = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    spots = db.relationship('ParkingSpot', backref='parking_lot', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ParkingLot {self.prime_location_name}>'

class ParkingSpot(db.Model):
    __tablename__ = 'parking_spots'
    
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lots.id'), nullable=False)
    status = db.Column(db.String(1), nullable=False, default='A')  # A = Available, O = Occupied
    
    reservations = db.relationship('Reservation', backref='parking_spot', lazy=True)
    
    def __repr__(self):
        return f'<ParkingSpot {self.id} in Lot {self.lot_id}>'

class Reservation(db.Model):
    __tablename__ = 'reservations'
    
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spots.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vehicle_number = db.Column(db.String(20), nullable=False)
    parking_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expected_end_time = db.Column(db.DateTime, nullable=True)
    leaving_timestamp = db.Column(db.DateTime, nullable=True)
    parking_cost = db.Column(db.Float, nullable=True)
    payment_status = db.Column(db.String(20), nullable=True)
    payment_mode = db.Column(db.String(20), nullable=True)
    payment_time = db.Column(db.DateTime, nullable=True)
    force_released = db.Column(db.Boolean, nullable=True, default=False)
    
    def __repr__(self):
        return f'<Reservation {self.id}>'
