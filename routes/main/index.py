from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from ..main import main_bp
from models import db, User, ParkingLot, Reservation, ParkingSpot
from datetime import datetime, timedelta
import json

@main_bp.route('/')
def index():
    available_spots = ParkingSpot.query.filter_by(status='A').count()
    return render_template('main/index.html', available_spots=available_spots) 