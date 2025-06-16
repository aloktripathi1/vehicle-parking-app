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

# 3. Run the app
python app.py
