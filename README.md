# Vehicle Parking App

A multi-user 4-wheeler parking management system built with Flask and SQLite.  
This project is part of **Modern Application Development I** at IITM.

## 👥 Roles

- **Admin**: Superuser who can manage parking lots and view all spots/users.
- **User**: Can register/login, reserve, park, and release spots.

## ⚙️ Tech Stack

- Flask (Python)
- SQLite (Programmatic DB setup)
- Jinja2 (Templating)
- HTML/CSS/Bootstrap (Frontend)
- Chart.js (Optional summary graphs)

## 🏁 How to Run

```bash
# 1. Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

<<<<<<< HEAD
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
=======
# 3. Run the app
python app.py
>>>>>>> 1fb5553 (Update README.md)
