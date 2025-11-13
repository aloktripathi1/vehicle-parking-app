# Vehicle Parking App

A multi-user 4-wheeler parking management system built with Flask and SQLite.  
This project is part of **Modern Application Development I** at IITM.

## 👥 Roles

- **Admin**: Superuser who can manage parking lots, view all spots/users, and access full parking history. Admin is automatically created on first run—no registration required.
  - Default credentials: `admin@parkease.com` / `admin123`
  - Credentials can be customized via environment variables (see Configuration below)
- **User**: Can register/login, reserve, park, and release spots.

## ⚙️ Tech Stack

- Flask (Python)
- SQLite (Programmatic DB setup via SQLAlchemy)
- Jinja2 (Templating)
- Bootstrap 5.3 (CSS Framework)
- Bootstrap Icons (Icons)
- HTML/CSS (Frontend - simplified, minimal custom styling)

## 📁 Project Structure

```
parking_app_23f3003225/
├── app.py                # Main application entry point
├── models.py             # Database models
├── forms.py              # WTForms definitions
├── utils.py              # Utility functions (e.g., timezone)
├── requirements.txt      # Python dependencies
├── README.md             # Project documentation
├── instance/
│   └── database.db       # SQLite database (auto-created)
├── migrations/           # Alembic migration files
├── routes/               # All Flask route blueprints
│   ├── admin/            # Admin routes (dashboard, lots, users, history, etc.)
│   ├── api/              # API endpoints (AJAX, data, etc.)
│   ├── main/             # Main/public routes (index, login, register)
│   └── user/             # User routes (dashboard, booking, profile)
├── static/               # Static assets
│   ├── parking_lot.jpg   # Images
│   └── parking_lot1.jpg
├── templates/            # Jinja2 HTML templates
│   ├── admin/            # Admin templates
│   │   ├── admin_dashboard.html
│   │   ├── admin_parking_lots.html
│   │   ├── admin_occupied_spots.html
│   │   ├── admin_users.html
│   │   ├── admin_parking_history.html
│   │   ├── admin_user_reservations.html
│   │   └── edit_parking_lot.html
│   ├── user/             # User templates
│   │   ├── user_dashboard.html
│   │   ├── user_parking_lots.html
│   │   ├── book_spot.html
│   │   └── edit_profile.html
│   └── main/             # Main/public templates
│       ├── base.html
│       ├── index.html
│       ├── login.html
│       ├── register.html
│       └── error.html
└── ...
```

## 🛣️ Route Organization

The application routes are organized into the following sections:

### Main Routes
- `/` - Home page
- `/login` - User/Admin login
- `/register` - New user registration
- `/logout` - Logout functionality

### User Routes
- `/user/dashboard` - User's main dashboard (active reservations, booking history, summary charts)
- `/user/edit_profile` - Update user profile
- `/user/parking_lots` - View available parking lots and spot availability
- `/user/book_spot` - Book a parking spot (auto-allotted)
- `/user/vacate_spot/<id>` - Vacate a parking spot

### Admin Routes
- `/admin/dashboard` - Admin's main dashboard (revenue, lot/spot/user stats, summary charts)
- `/admin/parking_lots` - Manage parking lots (add/edit/delete, adjust spot capacity)
- `/admin/users` - Manage users (view, edit, delete, see booking history)
- `/admin/occupied_spots` - View all currently occupied spots
- `/admin/parking_history` - **Parking History**: Complete log of all reservations ever made, with filters for date range, month/year, and parking lot
- `/admin/end_reservation/<id>` - End a reservation
- `/admin/edit_user/<id>` - Edit user details
- `/admin/delete_user/<id>` - Delete user
- `/admin/force_release/<id>` - Force release a spot

### API Routes
- `/api/parking_stats` - Get parking statistics
- `/api/user/<id>/reservations` - Get user's reservations
- `/api/users/search` - Search users
- `/api/check-active-booking` - Check active bookings
- `/api/book-parking` - Book parking spot
- `/api/parking-lots` - Get parking lots
- `/api/parking_lot/<id>/spots` - Get spots for a lot
- `/api/admin/user/<id>/reservations` - Get user reservations (admin)

## 🔑 Key Features

### User Features
- User registration and authentication
- View available parking lots and spots
- Book and vacate parking spots (auto-allocation)
- View booking history and summary charts
- Edit profile information

### Admin Features
- Hardcoded admin (no registration, always present)
- Manage parking lots (add/edit/delete, adjust spot count)
- View all users and their bookings
- Monitor occupied spots
- Force release parking spots
- View revenue and occupancy statistics (charts)
- **Parking History**: View a complete, permanent log of all reservations ever made, with advanced filters

## 🏁 How to Run

```bash
# 1. Create virtual environment (recommended)
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python app.py
```

The database and default admin user will be created automatically on first run.

## ⚙️ Configuration

### Admin Credentials
The default admin is automatically created when the app runs for the first time. You can customize the admin credentials using environment variables:

```bash
# Set custom admin credentials (optional)
export ADMIN_EMAIL="youradmin@example.com"
export ADMIN_PASSWORD="yourpassword"
export ADMIN_NAME="Your Admin Name"

# Then run the app
python app.py
```

**Default Admin Credentials** (if environment variables are not set):
- Email: `admin@parkease.com`
- Password: `admin123`
- Name: `Admin User`

**Note**: Admin registration is not allowed. The admin user is created programmatically only.

