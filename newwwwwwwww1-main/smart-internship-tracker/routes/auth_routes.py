"""
==============================================================
Smart Internship Tracker System — Auth Routes
==============================================================
REST API endpoints for user registration, login, and profile
for BOTH Students and Companies.
Passwords are hashed with bcrypt; auth uses JWT tokens.
==============================================================
"""

import re
from decimal import Decimal
from flask import Blueprint, request, jsonify, g
from mysql.connector import Error
from database.db_connection import get_db_connection
from services.auth_service import hash_password, verify_password, create_token
from services.auth_middleware import login_required

auth_bp = Blueprint("auth", __name__)

# ---------------------------------------------------------------
# Constants
# ---------------------------------------------------------------
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
MAX_NAME_LENGTH = 100
MAX_EMAIL_LENGTH = 150
MAX_DEPARTMENT_LENGTH = 100
MAX_COMPANY_NAME_LENGTH = 150
MAX_LOCATION_LENGTH = 150
MAX_INDUSTRY_LENGTH = 100
MIN_PASSWORD_LENGTH = 6
MAX_PASSWORD_LENGTH = 128


# ---------------------------------------------------------------
# POST /api/auth/register — Register a new account
# ---------------------------------------------------------------
@auth_bp.route("/api/auth/register", methods=["POST"])
def register():
    """Register a new student or company account."""
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "error": "Request body must be valid JSON",
        }), 400

    role = data.get("role", "student").strip().lower()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    errors = []
    if not email or not EMAIL_REGEX.match(email):
        errors.append("A valid email is required")
    if len(email) > MAX_EMAIL_LENGTH:
        errors.append("email must be at most 150 chars")
    if len(password) < MIN_PASSWORD_LENGTH:
        errors.append(f"password must be at least {MIN_PASSWORD_LENGTH} characters")
    if len(password) > MAX_PASSWORD_LENGTH:
        errors.append(f"password must be at most {MAX_PASSWORD_LENGTH} characters")

    if role not in ["student", "company"]:
        return jsonify({"success": False, "error": "role must be 'student' or 'company'"}), 400

    connection = get_db_connection()
    if connection is None:
        return jsonify({"success": False, "error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        password_hash = hash_password(password)

        if role == "student":
            name = (data.get("name") or "").strip()
            department = (data.get("department") or "").strip()
            cgpa = data.get("cgpa")
            
            if not name or len(name) > MAX_NAME_LENGTH:
                errors.append("name is required (max 100 chars)")
            if not department or len(department) > MAX_DEPARTMENT_LENGTH:
                errors.append("department is required (max 100 chars)")
            try:
                cgpa = float(cgpa)
                if cgpa < 0 or cgpa > 10:
                    errors.append("cgpa must be between 0 and 10")
            except (TypeError, ValueError):
                errors.append("cgpa must be a number between 0 and 10")

            if errors:
                return jsonify({"success": False, "errors": errors}), 400

            # Check if email exists
            cursor.execute("SELECT Student_ID FROM Students WHERE Email = %s", (email,))
            if cursor.fetchone():
                return jsonify({"success": False, "error": "An account with this email already exists"}), 409

            cursor.execute(
                """INSERT INTO Students (Name, Email, Password_Hash, Department, CGPA)
                   VALUES (%s, %s, %s, %s, %s)""",
                (name, email, password_hash, department, cgpa),
            )
            connection.commit()
            user_id = cursor.lastrowid
            
            token = create_token(user_id, name, email, role="student")
            
            return jsonify({
                "success": True,
                "message": "Student account created successfully",
                "data": {
                    "user_id": user_id,
                    "student_id": user_id,
                    "role": "student",
                    "name": name,
                    "email": email,
                    "department": department,
                    "token": token,
                },
            }), 201

        elif role == "company":
            company_name = (data.get("company_name") or "").strip()
            location = (data.get("location") or "").strip()
            industry_type = (data.get("industry_type") or "").strip()
            website = (data.get("website") or "").strip() or None

            if not company_name or len(company_name) > MAX_COMPANY_NAME_LENGTH:
                errors.append("company_name is required (max 150 chars)")
            if not location or len(location) > MAX_LOCATION_LENGTH:
                errors.append("location is required (max 150 chars)")
            if not industry_type or len(industry_type) > MAX_INDUSTRY_LENGTH:
                errors.append("industry_type is required (max 100 chars)")

            if errors:
                return jsonify({"success": False, "errors": errors}), 400

            # Check if email exists
            cursor.execute("SELECT Company_ID FROM Companies WHERE Email = %s", (email,))
            if cursor.fetchone():
                return jsonify({"success": False, "error": "A company account with this email already exists"}), 409

            cursor.execute(
                """INSERT INTO Companies (Company_Name, Email, Password_Hash, Location, Industry_Type, Website)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (company_name, email, password_hash, location, industry_type, website),
            )
            connection.commit()
            user_id = cursor.lastrowid

            token = create_token(user_id, company_name, email, role="company")

            return jsonify({
                "success": True,
                "message": "Company account created successfully",
                "data": {
                    "user_id": user_id,
                    "company_id": user_id,
                    "role": "company",
                    "name": company_name,
                    "email": email,
                    "location": location,
                    "industry_type": industry_type,
                    "token": token,
                },
            }), 201

    except Error as err:
        return jsonify({"success": False, "error": str(err)}), 500
    finally:
        cursor.close()
        connection.close()


# ---------------------------------------------------------------
# POST /api/auth/login — Log in with email and password
# ---------------------------------------------------------------
@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    """Authenticate a student or company and return a JWT token."""
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"success": False, "error": "Request body must be valid JSON"}), 400

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"success": False, "error": "Email and password are required"}), 400

    connection = get_db_connection()
    if connection is None:
        return jsonify({"success": False, "error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        
        # 1. Check Students
        cursor.execute(
            """SELECT Student_ID, Name, Email, Department, CGPA, Resume_Path, Password_Hash
               FROM Students WHERE Email = %s""",
            (email,),
        )
        student = cursor.fetchone()

        if student:
            pw_hash = student.get("Password_Hash") or ""
            if verify_password(password, pw_hash):
                token = create_token(student["Student_ID"], student["Name"], student["Email"], "student")
                return jsonify({
                    "success": True,
                    "message": "Login successful",
                    "data": {
                        "user_id": student["Student_ID"],
                        "student_id": student["Student_ID"],
                        "role": "student",
                        "name": student["Name"],
                        "email": student["Email"],
                        "department": student["Department"],
                        "cgpa": float(student["CGPA"]),
                        "resume_path": student["Resume_Path"],
                        "token": token,
                    },
                }), 200

        # 2. Check Companies
        cursor.execute(
            """SELECT Company_ID, Company_Name, Email, Location, Industry_Type, Website, Password_Hash
               FROM Companies WHERE Email = %s""",
            (email,),
        )
        company = cursor.fetchone()

        if company:
            pw_hash = company.get("Password_Hash") or ""
            if verify_password(password, pw_hash):
                token = create_token(company["Company_ID"], company["Company_Name"], company["Email"], "company")
                return jsonify({
                    "success": True,
                    "message": "Login successful",
                    "data": {
                        "user_id": company["Company_ID"],
                        "company_id": company["Company_ID"],
                        "role": "company",
                        "name": company["Company_Name"],
                        "email": company["Email"],
                        "location": company["Location"],
                        "industry_type": company["Industry_Type"],
                        "website": company["Website"],
                        "token": token,
                    },
                }), 200

        return jsonify({"success": False, "error": "Invalid email or password"}), 401

    except Error as err:
        return jsonify({"success": False, "error": str(err)}), 500
    finally:
        cursor.close()
        connection.close()


# ---------------------------------------------------------------
# GET /api/auth/me — Get current user/company profile
# ---------------------------------------------------------------
@auth_bp.route("/api/auth/me", methods=["GET"])
@login_required
def get_me():
    """Return the logged-in user's profile information."""
    user = g.current_user
    role = user["role"]
    connection = get_db_connection()
    if connection is None:
        return jsonify({"success": False, "error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        
        if role == "student":
            cursor.execute(
                """SELECT Student_ID AS user_id, Name AS name, Email AS email, Department AS department, 
                          CGPA AS cgpa, Resume_Path AS resume_path, Created_At
                   FROM Students WHERE Student_ID = %s""",
                (user["user_id"],),
            )
        elif role == "company":
            cursor.execute(
                """SELECT Company_ID AS user_id, Company_Name AS name, Email AS email, Location AS location, 
                          Industry_Type AS industry_type, Website AS website, Created_At
                   FROM Companies WHERE Company_ID = %s""",
                (user["user_id"],),
            )
        else:
            return jsonify({"success": False, "error": "Invalid role"}), 400

        profile = cursor.fetchone()

        if not profile:
            return jsonify({"success": False, "error": "User not found"}), 404

        # Convert non-serializable types and add role
        profile["role"] = role
        for key, value in profile.items():
            if hasattr(value, "isoformat"):
                profile[key] = value.isoformat()
            elif isinstance(value, Decimal):
                profile[key] = float(value)

        return jsonify({"success": True, "data": profile}), 200

    except Error as err:
        return jsonify({"success": False, "error": str(err)}), 500

    finally:
        cursor.close()
        connection.close()
