# ParkEase - Smart Parking Management System

ParkEase is a modern web-based parking management system that helps users find, book, and manage parking spots efficiently. The system provides a user-friendly interface for both parking lot administrators and regular users.

## Features

### For Users
- User registration and authentication
- Real-time parking spot availability
- Easy booking system
- Parking history tracking
- Cost analytics and statistics
- Profile management
- Dark/Light theme support

### For Administrators
- Comprehensive dashboard with analytics
- Parking lot management
- User management
- Revenue tracking
- Occupied spots monitoring
- Booking management

## Tech Stack

### Backend
- Flask 2.0.1
- Flask-Login 0.5.0
- Flask-SQLAlchemy 3.0.2
- Flask-WTF 0.15.1
- SQLAlchemy 1.4.41
- WTForms 2.3.3
- Werkzeug 2.0.1

### Frontend
- HTML5
- CSS3
- JavaScript (ES6+)
- Bootstrap 5.3.0
- Chart.js
- Font Awesome 6.0.0
- Google Fonts (Poppins, Montserrat, Open Sans)

### Database
- SQLite

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd parking_app
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

5. Run the application:
```bash
flask run
```

The application will be available at `http://localhost:5000`

## Project Structure

```
parking_app_23f3003225/
├── app.py              # Main application file
├── models.py           # Database models
├── forms.py            # Form definitions
├── static/            # Static files
│   ├── css/          # Stylesheets
│   ├── js/           # JavaScript files
│   └── images/       # Image assets
├── templates/         # HTML templates
├── instance/         # Instance-specific files
└── requirements.txt   # Project dependencies
```

## Usage

### User Access
1. Register a new account or login with existing credentials
2. Browse available parking lots
3. Book a parking spot
4. View booking history and analytics
5. Manage profile settings

### Admin Access
1. Login with admin credentials
2. Access the admin dashboard
3. Manage parking lots and users
4. Monitor occupied spots
5. View revenue analytics

## Features in Detail

### User Dashboard
- Active booking status
- Parking history
- Cost analytics
- Profile management
- Theme customization

### Admin Dashboard
- Revenue analytics
- User management
- Parking lot management
- Occupied spots monitoring
- Booking management

### Parking Lot Management
- Add/Edit parking lots
- Set pricing
- Monitor availability
- Track revenue

## Security Features
- Password hashing
- CSRF protection
- Session management
- Form validation
- Secure password handling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Bootstrap for the frontend framework
- Font Awesome for icons
- Chart.js for data visualization
- Flask community for the backend framework 
