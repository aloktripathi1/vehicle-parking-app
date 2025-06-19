from flask import Blueprint

admin_bp = Blueprint('admin', __name__)
 
from . import dashboard, parking_lots, edit_parking_lot, delete_parking_lot, users, occupied_spots, end_reservation, edit_user, delete_user, force_release
from . import parking_history 