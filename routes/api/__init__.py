from flask import Blueprint

api_bp = Blueprint('api', __name__)
 
from . import parking_stats, user_reservations, search_users, check_active_booking, book_parking, parking_lots, parking_lot_spots, admin_user_reservations 