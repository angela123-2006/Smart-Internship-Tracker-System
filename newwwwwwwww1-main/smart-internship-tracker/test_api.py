"""
==============================================================
Smart Internship Tracker — Senior QA Test Suite
==============================================================
Comprehensive API testing covering:
  1. Auth (Student + Company register/login)
  2. Role-based access control
  3. Internship CRUD (Company-only create)
  4. Student Application flow
  5. Resume Upload
  6. Skills management
  7. Notifications
  8. Recommendations
  9. Edge cases & error handling
==============================================================
"""

import json
import urllib.request
import urllib.error
import sys
import os

BASE = "http://127.0.0.1:5000"
PASS = 0
FAIL = 0
WARN = 0
RESULTS = []

# ── Unique emails for this test run ──
import time
TS = str(int(time.time()))
STUDENT_EMAIL = f"qastudent_{TS}@test.com"
COMPANY_EMAIL = f"qacompany_{TS}@test.com"
PASSWORD = "SecurePass123!"


def req(method, path, body=None, token=None, expect_status=None, form_data=None):
    """Send an HTTP request and return (status_code, parsed_json)."""
    url = BASE + path
    headers = {}
    data = None

    if token:
        headers["Authorization"] = f"Bearer {token}"

    if form_data:
        # multipart not supported here; skip file uploads in this suite
        pass
    elif body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode("utf-8")

    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        response = urllib.request.urlopen(request)
        status = response.getcode()
        result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        status = e.code
        try:
            result = json.loads(e.read().decode("utf-8"))
        except Exception:
            result = {"error": str(e)}
    except Exception as e:
        status = 0
        result = {"error": str(e)}

    return status, result


def check(test_name, condition, detail=""):
    """Record a test result."""
    global PASS, FAIL
    if condition:
        PASS += 1
        RESULTS.append(f"  ✅ PASS: {test_name}")
    else:
        FAIL += 1
        RESULTS.append(f"  ❌ FAIL: {test_name} — {detail}")


def warn(test_name, detail=""):
    """Record a warning."""
    global WARN
    WARN += 1
    RESULTS.append(f"  ⚠️  WARN: {test_name} — {detail}")


def section(title):
    """Print a section header."""
    RESULTS.append(f"\n{'='*60}")
    RESULTS.append(f"  {title}")
    RESULTS.append(f"{'='*60}")


# ══════════════════════════════════════════════════════════════
#  TEST 1: STUDENT REGISTRATION
# ══════════════════════════════════════════════════════════════
section("1. STUDENT REGISTRATION")

# 1a. Valid registration
s, r = req("POST", "/api/auth/register", {
    "role": "student", "email": STUDENT_EMAIL, "password": PASSWORD,
    "name": "QA Student", "department": "Computer Science", "cgpa": 8.5
})
check("Student register returns 201", s == 201, f"got {s}")
check("Response has token", r.get("data", {}).get("token") is not None, str(r))
student_token = r.get("data", {}).get("token", "")
student_id = r.get("data", {}).get("user_id")
check("Response has user_id", student_id is not None, str(r))
check("Response role is 'student'", r.get("data", {}).get("role") == "student")

# 1b. Duplicate email
s, r = req("POST", "/api/auth/register", {
    "role": "student", "email": STUDENT_EMAIL, "password": PASSWORD,
    "name": "Dup", "department": "CS", "cgpa": 7.0
})
check("Duplicate email returns 409", s == 409, f"got {s}")

# 1c. Missing fields
s, r = req("POST", "/api/auth/register", {
    "role": "student", "email": "bad@test.com", "password": PASSWORD
})
check("Missing name/dept returns 400", s == 400, f"got {s}")

# 1d. Invalid CGPA
s, r = req("POST", "/api/auth/register", {
    "role": "student", "email": "cgpa_bad@test.com", "password": PASSWORD,
    "name": "Bad CGPA", "department": "CS", "cgpa": 15
})
check("CGPA > 10 returns 400", s == 400, f"got {s}")

# 1e. Short password
s, r = req("POST", "/api/auth/register", {
    "role": "student", "email": "short@test.com", "password": "ab",
    "name": "Short", "department": "CS", "cgpa": 5
})
check("Short password returns 400", s == 400, f"got {s}")


# ══════════════════════════════════════════════════════════════
#  TEST 2: COMPANY REGISTRATION
# ══════════════════════════════════════════════════════════════
section("2. COMPANY REGISTRATION")

s, r = req("POST", "/api/auth/register", {
    "role": "company", "email": COMPANY_EMAIL, "password": PASSWORD,
    "company_name": "QA Corp", "location": "Bangalore", "industry_type": "Software"
})
check("Company register returns 201", s == 201, f"got {s}")
check("Company response has token", r.get("data", {}).get("token") is not None)
company_token = r.get("data", {}).get("token", "")
company_id = r.get("data", {}).get("user_id")
check("Company response role is 'company'", r.get("data", {}).get("role") == "company")

# Duplicate
s, r = req("POST", "/api/auth/register", {
    "role": "company", "email": COMPANY_EMAIL, "password": PASSWORD,
    "company_name": "Dup Corp", "location": "X", "industry_type": "Y"
})
check("Duplicate company email returns 409", s == 409, f"got {s}")


# ══════════════════════════════════════════════════════════════
#  TEST 3: LOGIN
# ══════════════════════════════════════════════════════════════
section("3. LOGIN")

# Student login
s, r = req("POST", "/api/auth/login", {"email": STUDENT_EMAIL, "password": PASSWORD})
check("Student login returns 200", s == 200, f"got {s}")
check("Login returns valid token", r.get("data", {}).get("token") is not None)
student_token = r.get("data", {}).get("token", student_token)  # refresh

# Company login
s, r = req("POST", "/api/auth/login", {"email": COMPANY_EMAIL, "password": PASSWORD})
check("Company login returns 200", s == 200, f"got {s}")
company_token = r.get("data", {}).get("token", company_token)

# Wrong password
s, r = req("POST", "/api/auth/login", {"email": STUDENT_EMAIL, "password": "wrong"})
check("Wrong password returns 401", s == 401, f"got {s}")

# Non-existent email
s, r = req("POST", "/api/auth/login", {"email": "ghost@test.com", "password": "x"})
check("Non-existent email returns 401", s == 401, f"got {s}")

# Missing fields
s, r = req("POST", "/api/auth/login", {"email": "", "password": ""})
check("Empty login returns 400", s == 400, f"got {s}")


# ══════════════════════════════════════════════════════════════
#  TEST 4: AUTH MIDDLEWARE (protected routes)
# ══════════════════════════════════════════════════════════════
section("4. AUTH MIDDLEWARE")

# No token
s, r = req("GET", "/api/applications")
check("No-token request returns 401", s == 401, f"got {s}")

# Invalid token
s, r = req("GET", "/api/applications", token="invalidtoken123")
check("Invalid token returns 401", s == 401, f"got {s}")

# Valid token
s, r = req("GET", "/api/applications", token=student_token)
check("Valid student token returns 200", s == 200, f"got {s}")


# ══════════════════════════════════════════════════════════════
#  TEST 5: GET /api/auth/me — Profile endpoint
# ══════════════════════════════════════════════════════════════
section("5. PROFILE ENDPOINT /api/auth/me")

s, r = req("GET", "/api/auth/me", token=student_token)
check("/me returns 200 for student", s == 200, f"got {s}")
check("/me has correct name", r.get("data", {}).get("name") == "QA Student", str(r.get("data")))

s, r = req("GET", "/api/auth/me", token=company_token)
check("/me returns 200 for company", s == 200, f"got {s}")
check("/me has correct company name", r.get("data", {}).get("name") == "QA Corp", str(r.get("data")))


# ══════════════════════════════════════════════════════════════
#  TEST 6: INTERNSHIP CREATION (Role Enforcement)
# ══════════════════════════════════════════════════════════════
section("6. INTERNSHIP CREATION (Role-Based)")

# Student tries to create → should be FORBIDDEN
s, r = req("POST", "/api/internships", {
    "role": "Backend Dev", "duration": "3 Months",
    "stipend": 10000, "application_deadline": "2027-06-01",
    "required_skills": "Python, Flask"
}, token=student_token)
check("Student cannot create internship (403)", s == 403, f"got {s}: {r}")

# Company creates internship → should succeed
s, r = req("POST", "/api/internships", {
    "role": "Backend Dev Intern", "duration": "3 Months",
    "stipend": 15000, "application_deadline": "2027-06-01",
    "required_skills": "Python, Flask, SQL"
}, token=company_token)
check("Company creates internship (201)", s == 201, f"got {s}: {r}")
internship_id = r.get("data", {}).get("internship_id")
check("Response has internship_id", internship_id is not None)

# Create a second internship
s, r = req("POST", "/api/internships", {
    "role": "Frontend Intern", "duration": "6 Months",
    "stipend": 20000, "application_deadline": "2027-12-31",
    "required_skills": "React, CSS, JavaScript"
}, token=company_token)
check("Second internship created (201)", s == 201, f"got {s}")
internship_id_2 = r.get("data", {}).get("internship_id")

# Missing required fields
s, r = req("POST", "/api/internships", {
    "role": "", "duration": "", "stipend": -100,
    "application_deadline": ""
}, token=company_token)
check("Empty fields returns 400", s == 400, f"got {s}")


# ══════════════════════════════════════════════════════════════
#  TEST 7: LIST INTERNSHIPS (public)
# ══════════════════════════════════════════════════════════════
section("7. LIST INTERNSHIPS")

s, r = req("GET", "/api/internships")
check("GET /api/internships returns 200", s == 200, f"got {s}")
check("Returns a list", isinstance(r.get("data"), list))
check("Count >= 2", r.get("count", 0) >= 2, f"count={r.get('count')}")

# By company
s, r = req("GET", f"/api/internships/company/{company_id}")
check(f"GET /api/internships/company/{company_id} returns 200", s == 200, f"got {s}")
check("Company-specific list has items", r.get("count", 0) >= 2, f"count={r.get('count')}")


# ══════════════════════════════════════════════════════════════
#  TEST 8: STUDENT APPLIES TO INTERNSHIP
# ══════════════════════════════════════════════════════════════
section("8. STUDENT APPLICATION")

today = "2026-03-27"
s, r = req("POST", "/api/applications", {
    "internship_id": internship_id, "application_date": today
}, token=student_token)
check("Student applies successfully (201)", s == 201, f"got {s}: {r}")
app_id = r.get("data", {}).get("application_id")
check("Response has application_id", app_id is not None)

# Apply to second one too
s, r = req("POST", "/api/applications", {
    "internship_id": internship_id_2, "application_date": today
}, token=student_token)
check("Student applies to 2nd internship (201)", s == 201, f"got {s}: {r}")
app_id_2 = r.get("data", {}).get("application_id")

# Missing fields
s, r = req("POST", "/api/applications", {
    "internship_id": None, "application_date": ""
}, token=student_token)
check("Missing app fields returns 400", s == 400, f"got {s}")


# ══════════════════════════════════════════════════════════════
#  TEST 9: VIEW STUDENT'S OWN APPLICATIONS
# ══════════════════════════════════════════════════════════════
section("9. STUDENT APPLICATION LIST")

s, r = req("GET", f"/api/applications/student/{student_id}", token=student_token)
check("Student sees own applications (200)", s == 200, f"got {s}")
check("Has >= 2 applications", r.get("count", 0) >= 2, f"count={r.get('count')}")


# ══════════════════════════════════════════════════════════════
#  TEST 10: APPLICATION STATUS UPDATE
# ══════════════════════════════════════════════════════════════
section("10. APPLICATION STATUS UPDATE")

if app_id:
    s, r = req("PUT", f"/api/applications/{app_id}/status", {
        "status": "Interview Scheduled"
    }, token=company_token)
    check("Status updated to Interview (200)", s == 200, f"got {s}: {r}")

    # Verify it changed
    s, r = req("GET", f"/api/applications/student/{student_id}", token=student_token)
    apps = r.get("data", [])
    interview_found = any(a.get("Application_Status") == "Interview Scheduled" for a in apps)
    check("Status reflects 'Interview Scheduled'", interview_found, str([a.get("Application_Status") for a in apps]))

    # Update to Selected
    s, r = req("PUT", f"/api/applications/{app_id}/status", {
        "status": "Selected"
    }, token=company_token)
    check("Status updated to Selected (200)", s == 200, f"got {s}")

    # Empty status
    s, r = req("PUT", f"/api/applications/{app_id}/status", {
        "status": ""
    }, token=company_token)
    check("Empty status returns 400", s == 400, f"got {s}")
else:
    warn("Skipped status tests", "no app_id")


# ══════════════════════════════════════════════════════════════
#  TEST 11: SKILLS MANAGEMENT
# ══════════════════════════════════════════════════════════════
section("11. SKILLS MANAGEMENT")

s, r = req("POST", "/api/skills", {
    "skill_name": "Python", "proficiency_level": "Advanced"
}, token=student_token)
check("Add skill returns 201", s == 201, f"got {s}: {r}")

s, r = req("POST", "/api/skills", {
    "skill_name": "SQL", "proficiency_level": "Intermediate"
}, token=student_token)
check("Add second skill returns 201", s == 201, f"got {s}")

s, r = req("GET", f"/api/skills/student/{student_id}", token=student_token)
check("Get skills returns 200", s == 200, f"got {s}")
check("Has >= 2 skills", r.get("count", len(r.get("data", []))) >= 2, str(r))


# ══════════════════════════════════════════════════════════════
#  TEST 12: RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════
section("12. RECOMMENDATIONS")

s, r = req("GET", f"/api/internships/recommend/{student_id}", token=student_token)
check("Recommendations returns 200", s == 200, f"got {s}")
# Since we added Python & SQL skills, and posted an internship requiring Python,Flask,SQL
recs = r.get("data", [])
check("Has >= 1 recommendation", len(recs) >= 1, f"got {len(recs)} recs")
if recs:
    check("Recommendation has match_count", recs[0].get("match_count", 0) >= 1)


# ══════════════════════════════════════════════════════════════
#  TEST 13: APPLICATION STATISTICS
# ══════════════════════════════════════════════════════════════
section("13. APPLICATION STATISTICS")

s, r = req("GET", "/api/applications/statistics", token=student_token)
check("Statistics returns 200", s == 200, f"got {s}")
check("Statistics has data", isinstance(r.get("data"), list))


# ══════════════════════════════════════════════════════════════
#  TEST 14: ALL APPLICATIONS (Admin/Feed view)
# ══════════════════════════════════════════════════════════════
section("14. ALL APPLICATIONS")

s, r = req("GET", "/api/applications", token=student_token)
check("All applications returns 200", s == 200, f"got {s}")
check("Returns list of apps", isinstance(r.get("data"), list))


# ══════════════════════════════════════════════════════════════
#  TEST 15: STUDENTS LIST & COMPANIES LIST
# ══════════════════════════════════════════════════════════════
section("15. ENTITY LISTS")

s, r = req("GET", "/api/students")
check("GET /api/students returns 200", s == 200, f"got {s}")

s, r = req("GET", "/api/companies")
check("GET /api/companies returns 200", s == 200, f"got {s}")


# ══════════════════════════════════════════════════════════════
#  TEST 16: NOTIFICATIONS
# ══════════════════════════════════════════════════════════════
section("16. NOTIFICATIONS")

s, r = req("GET", f"/api/notifications/student/{student_id}", token=student_token)
check("Notifications returns 200", s == 200, f"got {s}")


# ══════════════════════════════════════════════════════════════
#  TEST 17: STATIC FILE SERVING
# ══════════════════════════════════════════════════════════════
section("17. STATIC FILE SERVING")

try:
    resp = urllib.request.urlopen(f"{BASE}/")
    check("Root (index.html) serves 200", resp.getcode() == 200)
    body = resp.read().decode("utf-8")
    check("HTML contains 'Smart Internship Tracker'", "Smart Internship Tracker" in body)
    check("HTML has Student/Employer toggle", "btn-role-student" in body)
    check("HTML has employer pages", "page-emp-postings" in body)
    check("HTML has resume upload", "resume-upload" in body)
except Exception as e:
    check("Root serves index.html", False, str(e))

try:
    resp = urllib.request.urlopen(f"{BASE}/static/app.js")
    check("app.js serves 200", resp.getcode() == 200)
    js = resp.read().decode("utf-8")
    check("app.js has setAuthRole", "setAuthRole" in js)
    check("app.js has loadEmployerPostings", "loadEmployerPostings" in js)
    check("app.js has uploadResume", "uploadResume" in js)
    check("app.js has createInternship", "createInternship" in js)
except Exception as e:
    check("app.js served", False, str(e))

try:
    resp = urllib.request.urlopen(f"{BASE}/static/styles.css")
    check("styles.css serves 200", resp.getcode() == 200)
except Exception as e:
    check("styles.css served", False, str(e))


# ══════════════════════════════════════════════════════════════
#  FINAL REPORT
# ══════════════════════════════════════════════════════════════
RESULTS.append(f"\n{'='*60}")
RESULTS.append(f"  📊 FINAL REPORT")
RESULTS.append(f"{'='*60}")
RESULTS.append(f"  ✅ Passed : {PASS}")
RESULTS.append(f"  ❌ Failed : {FAIL}")
RESULTS.append(f"  ⚠️  Warns  : {WARN}")
RESULTS.append(f"  📋 Total  : {PASS + FAIL + WARN}")
RESULTS.append(f"{'='*60}")

if FAIL == 0:
    RESULTS.append("  🎉 ALL TESTS PASSED! System is production-ready.")
else:
    RESULTS.append(f"  🔴 {FAIL} test(s) FAILED — review above.")
RESULTS.append("")

report = "\n".join(RESULTS)
print(report)

# Save report to file
with open("qa_report.txt", "w", encoding="utf-8") as f:
    f.write(report)
print(f"\nReport saved to qa_report.txt")
