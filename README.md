# GeoPermit System — Mini Capstone

A web-based permit application system with GIS hazard validation.

---

## Tech Stack

| Layer    | Technology                        |
|----------|-----------------------------------|
| Backend  | Python Flask                      |
| Frontend | HTML, Bootstrap 5, Bootstrap Icons|
| Database | MySQL                             |
| Maps     | Leaflet.js + OpenStreetMap        |
| Charts   | Chart.js                          |

---

## Folder Structure

```
geopermit/
├── app.py              ← Flask entry point
├── config.py           ← Configuration (DB, secret key, uploads)
├── models.py           ← All database query helpers
├── requirements.txt
├── database.sql        ← Run this first to create DB + seed data
│
├── routes/
│   ├── auth.py         ← Login, Register, Logout
│   ├── dashboard.py    ← User & Admin dashboard + auth decorators
│   ├── permits.py      ← Apply, view, hazard API, requirements API
│   └── admin.py        ← Review applications, manage users
│
├── templates/
│   ├── base.html           ← Shared layout with sidebar
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html      ← User dashboard
│   ├── apply.html          ← Permit form + Leaflet map
│   ├── my_applications.html
│   ├── view_application.html
│   └── admin/
│       ├── dashboard.html
│       ├── applications.html
│       ├── review_application.html
│       └── users.html
│
└── static/
    ├── css/        ← (add custom overrides here if needed)
    ├── js/         ← (add custom scripts here if needed)
    └── uploads/    ← Uploaded documents saved here (auto-created)
```

---

## Setup Instructions

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

> On Ubuntu/Debian you may need:
> ```bash
> sudo apt install libmysqlclient-dev pkg-config
> ```

### 2. Create the MySQL database

```bash
mysql -u root -p < database.sql
```

### 3. Set the admin password

The SQL seeds an admin account but with a placeholder hash. To set the real password, run Python:

```python
from werkzeug.security import generate_password_hash
print(generate_password_hash('admin123'))
```

Then update the DB:

```sql
USE geopermit_db;
UPDATE users SET password_hash = '<paste hash here>' WHERE email = 'admin@geopermit.gov';
```

### 4. Configure database credentials

Edit `config.py` or set environment variables:

```bash
export MYSQL_USER=root
export MYSQL_PASSWORD=yourpassword
export MYSQL_DB=geopermit_db
export SECRET_KEY=change-this-in-production
```

### 5. Configure email (optional)

If you want GeoPermit to send notification emails, set SMTP credentials before starting the app. For Gmail SMTP, use an app password and set the sender to the same Gmail account:

```bash
export MAIL_SERVER=smtp.gmail.com
export MAIL_PORT=587
export MAIL_USE_TLS=True
export MAIL_USERNAME=youremail@gmail.com
export MAIL_PASSWORD=your-gmail-app-password
export MAIL_DEFAULT_SENDER='GeoPermit System <youremail@gmail.com>'
```

If `MAIL_USERNAME` and `MAIL_PASSWORD` are not set, email delivery will be disabled and the app will continue running.

### 6. Run the app

```bash
python app.py
```

Visit: http://localhost:5000

---

## Default Accounts (after setup)

| Role  | Email                   | Password  |
|-------|-------------------------|-----------|
| Admin | admin@geopermit.gov     | admin123  |

Register new user accounts from the /register page.

---

## Key Features

### GIS Hazard Validation
- User pins a location on the Leaflet map
- Flask backend checks if coordinates fall within any hazard zone using the Haversine formula
- Red marker + warning banner shown if hazard zone detected
- Hazard info stored with the application record

### Smart Requirement Suggestion
- When the user selects a permit type, the required documents list is fetched via API
- Displayed before the file upload input

### Analytics Dashboard (Admin)
- Doughnut chart showing application status distribution
- Stat cards for totals, hazard zone count, user count

### CRUD Operations
- Create: user registration, permit application submission
- Read: dashboard, application list, single application view
- Update: admin approve/reject with remarks
- Delete: admin can remove non-admin users

---

## Team Task Division

| Member | Responsibility                            |
|--------|-------------------------------------------|
| 1      | `templates/` — All HTML pages             |
| 2      | `app.py`, `config.py`, `routes/`          |
| 3      | `database.sql`, `models.py`               |
| 4      | GIS map in `apply.html`, hazard check API |
