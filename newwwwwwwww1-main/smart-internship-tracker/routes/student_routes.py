"""
==============================================================
Smart Internship Tracker System — Student Routes
==============================================================
REST API endpoints for Student operations.
==============================================================
"""

import re
import os
import uuid
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify, g
from database.db_connection import get_db_connection
from models.student_model import (
    create_student,
    get_all_students,
    get_student_by_id,
)
from services.auth_middleware import login_required, role_required

# Blueprint lets us organize routes into separate files
student_bp = Blueprint("students", __name__)

# ---------------------------------------------------------------
# Constants
# ---------------------------------------------------------------
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
MAX_NAME_LENGTH = 100
MAX_EMAIL_LENGTH = 150
MAX_DEPARTMENT_LENGTH = 100

# ---------------------------------------------------------------
# POST /api/students/resume — Upload a resume PDF (Auth: Student)
# ---------------------------------------------------------------
@student_bp.route("/api/students/resume", methods=["POST"])
@role_required("student")
def api_upload_resume():
    """Upload a resume PDF for the logged-in student."""
    if "resume" not in request.files:
        return jsonify({"success": False, "error": "No file part"}), 400
    
    file = request.files["resume"]
    if file.filename == "":
        return jsonify({"success": False, "error": "No selected file"}), 400
    
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"success": False, "error": "Only PDF files are allowed"}), 400

    # Ensure secure filename and uniqueness
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads", "resumes")
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, unique_filename)
    file.save(file_path)

    relative_path = f"/uploads/{unique_filename}"

    # Update DB
    connection = get_db_connection()
    if connection is None:
        return jsonify({"success": False, "error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor()
        cursor.execute("UPDATE Students SET Resume_Path = %s WHERE Student_ID = %s", (relative_path, g.current_user["user_id"]))
        connection.commit()
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

    return jsonify({
        "success": True, 
        "message": "Resume uploaded successfully", 
        "data": {"resume_path": relative_path}
    }), 200


# ---------------------------------------------------------------
# POST /api/students — Create a new student
# ---------------------------------------------------------------
@student_bp.route("/api/students", methods=["POST"])
def api_create_student():
    """Create a new student record."""
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "error": "Request body must be valid JSON",
        }), 400

    # --- Input validation ---
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    department = (data.get("department") or "").strip()
    cgpa = data.get("cgpa")

    errors = []
    if not name or len(name) > MAX_NAME_LENGTH:
        errors.append("name is required (max 100 chars)")
    if not email or not EMAIL_REGEX.match(email):
        errors.append("A valid email is required")
    if len(email) > MAX_EMAIL_LENGTH:
        errors.append("email must be at most 150 chars")
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

    # --- Create the student ---
    result = create_student(name, email, department, cgpa)

    if result["success"]:
        return jsonify({
            "success": True,
            "message": "Student created successfully",
            "data": {"student_id": result["student_id"]},
        }), 201
    else:
        return jsonify({
            "success": False,
            "error": result["error"],
        }), 400


# ---------------------------------------------------------------
# GET /api/students — List all students
# ---------------------------------------------------------------
@student_bp.route("/api/students", methods=["GET"])
def api_get_students():
    """Retrieve all students (potentially sensitive, usually admin only)."""
    students = get_all_students()
    return jsonify({
        "success": True,
        "data": students,
        "count": len(students),
    }), 200


# ---------------------------------------------------------------
# GET /api/students/<id> — Get a single student
# ---------------------------------------------------------------
@student_bp.route("/api/students/<int:student_id>", methods=["GET"])
def api_get_student(student_id):
    """Retrieve a student by ID."""
    student = get_student_by_id(student_id)

    if student is None:
        return jsonify({
            "success": False,
            "error": "Student not found",
        }), 404

    return jsonify({"success": True, "data": student}), 200
