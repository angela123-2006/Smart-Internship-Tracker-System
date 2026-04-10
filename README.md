# Smart-Internship-Tracker-System
DBMS-based internship tracking system
🎓 Smart Internship Tracker System
![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.x-black?logo=flask)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange?logo=mysql&logoColor=white)
![JWT](https://img.shields.io/badge/Auth-JWT-green)
![License](https://img.shields.io/badge/License-MIT-purple)
> A full-stack internship management platform connecting **Students**, **Companies**, and a **College Placement Cell** — built as a DBMS project showcasing production-grade database engineering.
---
📌 What is this?
The Smart Internship Tracker allows:
🧑‍🎓 Students — browse internships, apply, track status, upload resumes, manage skills
🏢 Companies — post internship openings, review applicants, update application status
🏫 Placement Cell — monitor all placement activity from a unified coordinator dashboard
---
⚙️ Technology Stack
Technology	Purpose
Python 3.8+	Core backend language
Flask	Web framework — routing & HTTP
MySQL 8.0+	Relational database
mysql-connector-python	MySQL driver with connection pooling
PyJWT	JSON Web Token generation & verification
bcrypt	Password hashing (12 salt rounds)
Flask-SocketIO	Real-time notifications via WebSockets
Flask-Limiter	Rate limiting against brute-force
Flask-CORS	Cross-Origin Resource Sharing
Vanilla JS / HTML / CSS	Frontend SPA (glassmorphism UI)
---
🗂️ Project Structure
```
Smart-Internship-Tracker/
├── app.py                    # Entry point — Flask app, Blueprints, SocketIO
├── config.py                 # Environment config (reads .env)
├── .env.example              # Credential template (never commit .env!)
├── requirements.txt          # All Python dependencies
├── test_api.py               # 70 automated API tests
│
├── database/
│   ├── db_connection.py      # MySQL connection pool (pool_size=5)
│   └── schema.sql            # Tables, constraints, indexes, sample data
│
├── models/                   # Data Access Layer (SQL functions)
│   ├── student_model.py
│   ├── company_model.py
│   ├── internship_model.py
│   ├── application_model.py
│   ├── skill_model.py
│   └── notification_model.py
│
├── routes/                   # Flask Blueprints (API Controllers)
│   ├── auth_routes.py
│   ├── student_routes.py
│   ├── company_routes.py
│   ├── internship_routes.py
│   ├── application_routes.py
│   ├── skill_routes.py
│   └── notification_routes.py
│
├── services/                 # Business Logic & Middleware
│   ├── auth_service.py       # JWT creation, bcrypt hashing
│   └── auth_middleware.py    # @login_required, @role_required decorators
│
├── static/                   # Frontend (View Layer)
│   ├── index.html
│   ├── app.js
│   └── styles.css
│
└── uploads/resumes/          # Student PDF resumes (path stored in DB)
```
---
🗄️ Database Schema
Six tables with full constraint coverage:
```
Students ──< Applications >── Internships ──< Companies
Students ──< Skills
Students ──< Notifications
```
Key constraints demonstrated:
`CHECK (CGPA >= 0 AND CGPA <= 10)` — rejects invalid data at DB level
`UNIQUE KEY (Student_ID, Internship_ID)` — prevents duplicate applications
`ON DELETE CASCADE` — removes orphan records automatically
`ENUM` on Application_Status and Proficiency_Level
`B-Tree INDEX` on `Application_Deadline` — O(log n) deadline queries
---
🔒 Security Architecture
Feature	Implementation
Password Hashing	bcrypt, 12 salt rounds — never plain text
Authentication	JWT tokens, 24h expiry, stateless
Authorization	`@login_required` + `@role_required` decorators (RBAC)
SQL Injection Prevention	Parameterized queries (`%s` placeholders) everywhere
Rate Limiting	200 req/min global · 10/min login · 5/min register
XSS Protection	All user input HTML-escaped before rendering
---
🚀 Getting Started
Prerequisites
Python 3.8+
MySQL 8.0+
Installation
```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/Smart-Internship-Tracker-System.git
cd Smart-Internship-Tracker-System

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.example .env
# Edit .env with your MySQL credentials and a JWT secret key

# 4. Set up the database
mysql -u root -p < database/schema.sql

# 5. Run the server
python app.py
```
Open `http://127.0.0.1:5000` in your browser.
---
📡 API Reference
Base URL: `http://127.0.0.1:5000`  
All responses: `{ "success": true/false, "data": {...} }`
Auth
Method	Endpoint	Auth	Description
POST	`/api/auth/register`	❌	Register as Student or Company
POST	`/api/auth/login`	❌	Login — returns JWT token
GET	`/api/auth/me`	✅	Get current user profile
Internships
Method	Endpoint	Role	Description
POST	`/api/internships`	Company	Create internship posting
GET	`/api/internships`	Any	List all internships
GET	`/api/internships/recommend/<id>`	Student	AI skill-matched recommendations
Applications
Method	Endpoint	Role	Description
POST	`/api/applications`	Student	Apply for internship
GET	`/api/applications/student/<id>`	Student	View own applications
PUT	`/api/applications/<id>/status`	Company	Update status
GET	`/api/applications/statistics`	Any	Status breakdown counts
---
🧠 DBMS Concepts Showcased
Connection Pooling — `pool_size=5` handles concurrent requests without crashing
Parameterized Queries — every SQL statement is injection-proof at the driver level
Cascading Foreign Keys — referential integrity enforced by MySQL, not application code
CHECK Constraints — invalid CGPA rejected before the row is written
B-Tree Indexing — `Application_Deadline` index reduces 10,000-row scan to ~14 comparisons
UNIQUE Constraints — duplicate applications rejected at the database level
ENUM Types — application status and skill proficiency restricted to valid values
MVC Architecture — clean separation: `models/` → `routes/` → `static/`
---
🧪 Running Tests
```bash
python test_api.py
```
70 automated tests covering: registration, login, RBAC enforcement (403 checks), internship CRUD, applications, skills, recommendations, notifications, and static file serving.
---
📊 Key SQL Queries
<details>
<summary>Master JOIN — 4 tables at once</summary>
```sql
SELECT
    s.Name AS 'Student Name', s.CGPA,
    c.Company_Name AS 'Applied To',
    i.Title AS 'Role', i.Stipend,
    a.Application_Status, a.Application_Date
FROM Students s
JOIN Applications a ON s.Student_ID = a.Student_ID
JOIN Internships i ON a.Internship_ID = i.Internship_ID
JOIN Companies c ON i.Company_ID = c.Company_ID
ORDER BY a.Application_Date DESC;
```
</details>
<details>
<summary>Application Statistics (GROUP BY)</summary>
```sql
SELECT
    Application_Status AS 'Status',
    COUNT(*) AS 'Count',
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Applications), 2) AS 'Percentage %'
FROM Applications
GROUP BY Application_Status
ORDER BY COUNT(*) DESC;
```
</details>
---
📄 License
MIT License — feel free to use, modify, and distribute.
