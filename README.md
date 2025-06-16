# Vehicle Parking App

A multi-user 4-wheeler parking management system built with Flask and SQLite.  
This project is part of **Modern Application Development I** at IITM BS.

## 👥 Roles

- **Admin**: Superuser who can manage parking lots and view all spots/users.
- **User**: Can register/login, reserve, park, and release spots.

## ⚙️ Tech Stack

- Flask (Python)
- SQLite (Programmatic DB setup)
- Jinja2 (Templating)
- HTML/CSS/Bootstrap (Frontend)
- Chart.js (Optional summary graphs)

## 📁 Project Structure

```
parking_app/
├── app.py              # Main application file with all routes
├── models.py           # Database models and relationships
├── forms.py            # Form definitions using WTForms
├── requirements.txt    # Project dependencies
├── static/            # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
└── templates/         # HTML templates

```

## 🛣️ Route Organization

The application routes in `app.py` are organized into the following sections:

### 1. Utility / Error Handling / Misc
- `@app.errorhandler(500)` - Internal server error handler
- `@login_manager.user_loader` - User loader for Flask-Login
- `has_active_booking()` - Utility function to check active bookings

### 2. Main Routes
- `/` - Home page
- `/login` - User/Admin login
- `/register` - New user registration
- `/logout` - Logout functionality

### 3. User Routes
- `/user/dashboard` - User's main dashboard
  - Shows active reservations
  - Displays booking history
  - Shows total spent and time statistics
- `/user/edit_profile` - Update user profile
  - Edit personal information
  - Update address and pincode
- `/user/parking_lots` - View available parking lots
  - List all parking locations
  - Show spot availability
- `/book_spot` - Book a parking spot
  - Reserve available spots
  - Handle payment calculation
- `/user/vacate_spot/<id>` - Vacate a parking spot
  - End current parking session
  - Calculate final charges

### 4. Admin Routes
- `/admin/dashboard` - Admin's main dashboard
  - Revenue statistics
  - Parking lot overview
  - User statistics
- `/admin/parking_lots` - Manage parking lots
  - Add new parking lots
  - View all locations
- `/admin/parking_lot/<id>/edit` - Edit parking lot
  - Update location details
  - Modify pricing
  - Adjust spot capacity
- `/admin/parking_lot/<id>/delete` - Delete parking lot
- `/admin/users` - Manage users
  - View all registered users
  - User statistics and history
- `/admin/occupied_spots` - View occupied spots
  - Monitor current usage
  - Track active reservations
- `/admin/end_reservation/<id>` - End a reservation
- `/admin/edit_user/<id>` - Edit user details
- `/admin/delete_user/<id>` - Delete user
- `/admin/force_release/<id>` - Force release a spot

### 5. API Routes
- `/api/parking_stats` - Get parking statistics
  - Revenue data
  - Occupancy rates
- `/api/user/<id>/reservations` - Get user's reservations
  - Booking history
  - Active bookings
- `/api/users/search` - Search users
  - Filter by name/email
  - Pagination support
- `/api/check-active-booking` - Check active bookings
- `/api/book-parking` - Book parking spot
- `/api/parking-lots` - Get parking lots
  - List all locations
  - Availability status
- `/api/parking_lot/<id>/spots` - Get spots for a lot
  - Spot status
  - Pricing information
- `/api/admin/user/<id>/reservations` - Get user reservations (admin)
  - Detailed booking history
  - Payment information

## 🔑 Key Features

### User Features
- User registration and authentication
- View available parking spots
- Book and vacate parking spots
- View booking history
- Edit profile information

### Admin Features
- Manage parking lots (add/edit/delete)
- View all users and their bookings
- Monitor occupied spots
- Force release parking spots
- View revenue statistics
- Manage user accounts

## 🏁 How to Run

```bash
# 1. Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python app.py
```

## 🔒 Default Admin Credentials
- Username: `admin`
- Password: `admin123`

## 📝 Notes
- The application uses SQLite as the database, which is automatically initialized on first run
- Admin user is created automatically if it doesn't exist
- All monetary values are in Indian Rupees (₹)
- Parking costs are calculated based on hourly rates set by the admin
