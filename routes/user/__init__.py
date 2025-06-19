from flask import Blueprint

user_bp = Blueprint('user', __name__)
 
from . import dashboard, edit_profile, parking_lots, book_spot, vacate_spot 