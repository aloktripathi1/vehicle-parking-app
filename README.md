# 🚗 Vehicle Parking System

A web-based application to efficiently manage parking lots and reservations. This system provides two main portals — one for users to reserve and release parking spots, and another for administrators to manage parking infrastructure and monitor real-time statistics.

---

## 📌 Features

### 🔐 Authentication
- User Signup with name, email, phone number, address, and PIN code
- User Login with email and password
- Admin access (no registration required)

---

### 🧑‍💼 Admin Functionalities
Accessible through the **Admin Dashboard**:

- 🔧 **Manage Parking Lots**
  - Add new parking lots
  - Edit or update existing lots
  - Set lot capacity and availability
  
- 🚗 **View/Delete Parking Spots**
  - Monitor real-time spot usage
  - View details of occupied spots
  - Delete or reset parking spots manually

- 🔎 **Search**
  - Search for parking lots by name or location

- 📊 **Summary & Analytics**
  - Visual charts displaying lot usage
  - View registered user statistics
  - Identify underused or overused lots

- 👥 **Manage Users**
  - View and manage all registered users
  - Edit user profiles if required

---

### 🙋‍♂️ User Functionalities
Accessible through the **User Dashboard**:

- 📜 **Booking History**
  - View recent booking and release history

- 📅 **Book a Parking Spot**
  - Select parking lot and slot
  - Input vehicle number and reserve a spot

- 🗓️ **Release Parking Spot**
  - End a booking manually and free the spot

- 🔍 **Search for Nearby Parking**
  - Search by location name or pin code

- 📊 **User Summary**
  - View visual summary of personal parking history

---

## 🧑‍💻 Tech Stack

| Frontend       | Backend        | Database     | Others                |
|----------------|----------------|--------------|------------------------|
| HTML, CSS, JS  | Node.js / Flask / Django (choose one) | MySQL / MongoDB | Chart.js / D3.js (for analytics) |

---

## 🗂️ Project Structure Suggestion

```

/vehicle-parking-system/
├── backend/
│   └── server.js / app.py
├── frontend/
│   ├── index.html
│   ├── login.html
│   ├── admin\_dashboard.html
│   └── user\_dashboard.html
├── public/
│   └── css/
│       └── styles.css
├── database/
│   └── schema.sql / models.py
├── assets/
│   └── images, icons, etc.
└── README.md

````

---

## 🚀 How to Run the Project

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/vehicle-parking-system.git
   cd vehicle-parking-system
````

2. **Setup backend**

   * Install dependencies

     ```bash
     npm install     # for Node.js
     pip install -r requirements.txt  # for Python Flask
     ```

   * Run the server
     npm start       # Node.js
     python app.py   # Flask


3. **Start frontend**

   * Open `index.html` in your browser or serve using `Live Server`.

4. **Access Application**

   * Navigate to `localhost:3000` or your local server port.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
