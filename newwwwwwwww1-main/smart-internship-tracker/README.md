# 🎓 Smart Internship Tracker System

A full-stack platform that connects **Students**, **Companies**, and the **College Placement Cell**. Companies post internships, students apply and track status, and coordinators monitor placement activity — all through a professional LinkedIn-inspired UI.

Built with **Python · Flask · MySQL · Vanilla JS** for a DBMS project.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **Role-Based Auth** | JWT authentication with bcrypt password hashing. Separate Student & Company flows |
| **Student Dashboard** | Browse internships, apply, track applications, manage skills, get AI recommendations |
| **Company Dashboard** | Post internships, view applicants, update statuses (Selected/Rejected), download resumes |
| **Resume Upload** | Students upload PDF resumes; companies can view them per applicant |
| **Skill Matching** | Recommendation engine matches student skills to internship requirements |
| **Real-Time Updates** | SocketIO broadcasts new applications and status changes instantly |
| **LinkedIn-Style UI** | Professional glassmorphism design with responsive layout |
| **Automated Testing** | 70 API tests covering all endpoints (`test_api.py`) |

---

## 📁 Project Structure

```
smart-internship-tracker/
├── app.py                    # Flask application entry point
├── config.py                 # Environment-based configuration
├── requirements.txt          # Python dependencies
├── test_api.py               # Automated API test suite (70 tests)
├── .env.example              # Template for environment variables
├── .gitignore                # Git exclusions
│
├── database/
│   ├── __init__.py
│   ├── db_connection.py      # MySQL connection pool
│   └── schema.sql            # Database schema + sample data
│
├── models/                   # Data access layer (SQL queries)
│   ├── __init__.py
│   ├── student_model.py
│   ├── company_model.py
│   ├── internship_model.py
│   ├── application_model.py
│   ├── skill_model.py
│   └── notification_model.py
│
├── routes/                   # REST API endpoints
│   ├── __init__.py
│   ├── auth_routes.py        # Registration, login, profile (/api/auth/*)
│   ├── student_routes.py     # Student CRUD + resume upload
│   ├── company_routes.py     # Company CRUD
│   ├── internship_routes.py  # Internship CRUD + recommendations
│   ├── application_routes.py # Applications + status updates
│   ├── skill_routes.py       # Skill management
│   └── notification_routes.py
│
├── services/
│   ├── __init__.py
│   ├── auth_service.py       # JWT creation/verification, bcrypt hashing
│   └── auth_middleware.py    # @login_required and @role_required decorators
│
├── static/                   # Frontend (served by Flask)
│   ├── index.html            # Main SPA with role-based views
│   ├── app.js                # Frontend logic and API integration
│   └── styles.css            # LinkedIn-inspired CSS
│
└── uploads/resumes/          # Uploaded resume PDFs
```

---

## 🚀 Setup & Installation

### Prerequisites

| Tool   | Version | Download |
|--------|---------|----------|
| Python | 3.8+    | https://www.python.org/downloads/ |
| MySQL  | 8.0+    | https://dev.mysql.com/downloads/installer/ |

### Step 1 — Clone & Install Dependencies

```bash
git clone https://github.com/YOUR_USERNAME/smart-internship-tracker.git
cd smart-internship-tracker

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
```

### Step 2 — Configure Environment

```bash
copy .env.example .env         # Windows
# cp .env.example .env         # macOS/Linux
```

Edit `.env` with your MySQL credentials:

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=internship_tracker
SECRET_KEY=your-secret-key-change-this
```

### Step 3 — Create Database

Open MySQL Workbench and execute `database/schema.sql`, or run:

```bash
mysql -u root -p < database/schema.sql
```

### Step 4 — Start the Server

```bash
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

---

## 📡 API Reference

> **Base URL:** `http://127.0.0.1:5000`
>
> All responses: `{ "success": true|false, "data": {...}, "message": "...", "error": "..." }`

### 🔐 Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/register` | ❌ | Register as Student or Company |
| POST | `/api/auth/login` | ❌ | Login and get JWT token |
| GET | `/api/auth/me` | ✅ | Get current user profile |

### 💼 Internships

| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| POST | `/api/internships` | ✅ | Company | Create internship posting |
| GET | `/api/internships` | ❌ | — | List all internships |
| GET | `/api/internships/company/<id>` | ❌ | — | Internships by company |
| GET | `/api/internships/recommend/<id>` | ✅ | Student | Skill-based recommendations |

### 📝 Applications

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/applications` | ✅ | Apply for an internship |
| GET | `/api/applications` | ✅ | All applications |
| GET | `/api/applications/student/<id>` | ✅ | Student's own applications |
| PUT | `/api/applications/<id>/status` | ✅ | Update status |
| GET | `/api/applications/statistics` | ✅ | Status breakdown counts |

### 🛠️ Skills & Notifications

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/skills` | ✅ | Add a skill |
| GET | `/api/skills/student/<id>` | ✅ | Get student's skills |
| POST | `/api/students/resume` | ✅ | Upload resume (PDF) |
| GET | `/api/notifications/student/<id>` | ✅ | Get notifications |

---

## 🗄️ Database Schema (ER Diagram)

```
Students ──────< Skills
    │
    └──────< Applications >────── Internships >────── Companies
    │
    └──────< Notifications
```

| Table | Primary Key | Foreign Keys |
|-------|-------------|--------------|
| Students | Student_ID | — |
| Companies | Company_ID | — |
| Internships | Internship_ID | Company_ID → Companies |
| Applications | Application_ID | Student_ID → Students, Internship_ID → Internships |
| Skills | Skill_ID | Student_ID → Students |
| Notifications | Notification_ID | Student_ID → Students |

---

## 🧪 Testing

### Automated Tests (70 tests)

```bash
python test_api.py
```

Covers: Registration, Login, RBAC, Internship CRUD, Applications, Skills, Recommendations, Notifications, and Static Files.

---

## 📌 Security Features

- ✅ Passwords hashed with **bcrypt** (12 rounds)
- ✅ JWT tokens with 24h expiry
- ✅ Role-based access control (`@role_required`)
- ✅ Parameterized SQL queries (prevents SQL injection)
- ✅ Input validation on all endpoints
- ✅ CORS and rate limiting configured
- ✅ XSS protection via HTML escaping in frontend

---

## 📄 License

This project is for educational purposes (DBMS project submission).
