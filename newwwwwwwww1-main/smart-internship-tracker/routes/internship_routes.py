"""
==============================================================
Smart Internship Tracker System — Internship Routes
==============================================================
REST API endpoints for Internship operations, including
a recommendation endpoint based on skill matching.
Emits real-time events on new postings.
==============================================================
"""

from flask import Blueprint, request, jsonify, g
from models.internship_model import (
    create_internship,
    get_all_internships,
    get_internships_by_company,
    get_recommended_internships,
)
from services.auth_middleware import login_required, role_required

internship_bp = Blueprint("internships", __name__)

# ---------------------------------------------------------------
# Constants
# ---------------------------------------------------------------
MAX_ROLE_LENGTH = 150
MAX_SKILLS_LENGTH = 500
MAX_DURATION_LENGTH = 50


def _emit_realtime(event, data):
    """Emit a SocketIO event for real-time updates."""
    try:
        from app import socketio
        socketio.emit(event, data)
    except Exception:
        pass


# ---------------------------------------------------------------
# POST /api/internships — Create a new internship
# ---------------------------------------------------------------
@internship_bp.route("/api/internships", methods=["POST"])
@role_required("company")
def api_create_internship():
    """Create a new internship posting."""
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "error": "Request body must be valid JSON",
        }), 400

    # --- Input validation ---
    company_id = g.current_user["company_id"]
    role = (data.get("role") or "").strip()
    required_skills = (data.get("required_skills") or "").strip()
    duration = (data.get("duration") or "").strip()
    stipend = data.get("stipend", 0)
    deadline = (data.get("application_deadline") or "").strip()

    errors = []
    if not company_id or not isinstance(company_id, int):
        errors.append("company_id is required and must be an integer")
    if not role or len(role) > MAX_ROLE_LENGTH:
        errors.append("role is required (max 150 chars)")
    if len(required_skills) > MAX_SKILLS_LENGTH:
        errors.append("required_skills must be at most 500 chars")
    if not duration or len(duration) > MAX_DURATION_LENGTH:
        errors.append("duration is required (max 50 chars)")
    if not deadline:
        errors.append("application_deadline is required (YYYY-MM-DD)")

    try:
        stipend = float(stipend)
        if stipend < 0:
            errors.append("stipend cannot be negative")
    except (TypeError, ValueError):
        errors.append("stipend must be a number")

    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    # --- Create the internship ---
    result = create_internship(
        company_id, role, required_skills,
        duration, stipend, deadline,
    )

    if result["success"]:
        _emit_realtime("internship_posted", {
            "internship_id": result["internship_id"],
            "role": role,
            "posted_by": g.current_user["name"],
        })

        return jsonify({
            "success": True,
            "message": "Internship created successfully",
            "data": {"internship_id": result["internship_id"]},
        }), 201
    else:
        return jsonify({"success": False, "error": result["error"]}), 400


# ---------------------------------------------------------------
# GET /api/internships — List all internships (public)
# ---------------------------------------------------------------
@internship_bp.route("/api/internships", methods=["GET"])
def api_get_internships():
    """Retrieve all internships with company details."""
    internships = get_all_internships()

    for item in internships:
        for key, value in item.items():
            if hasattr(value, "isoformat"):
                item[key] = value.isoformat()

    return jsonify({
        "success": True,
        "data": internships,
        "count": len(internships),
    }), 200


# ---------------------------------------------------------------
# GET /api/internships/company/<id> — Internships by company
# ---------------------------------------------------------------
@internship_bp.route("/api/internships/company/<int:company_id>",
                     methods=["GET"])
def api_get_internships_by_company(company_id):
    """Retrieve internships for a specific company."""
    internships = get_internships_by_company(company_id)

    for item in internships:
        for key, value in item.items():
            if hasattr(value, "isoformat"):
                item[key] = value.isoformat()

    return jsonify({
        "success": True,
        "data": internships,
        "count": len(internships),
    }), 200


# ---------------------------------------------------------------
# GET /api/internships/recommend/<student_id>
# ---------------------------------------------------------------
@internship_bp.route("/api/internships/recommend/<int:student_id>",
                     methods=["GET"])
@login_required
def api_recommend_internships(student_id):
    """
    Return internships where the student's skills match
    the required skills (simple recommendation engine).
    """
    recommendations = get_recommended_internships(student_id)

    for item in recommendations:
        for key, value in item.items():
            if hasattr(value, "isoformat"):
                item[key] = value.isoformat()

    return jsonify({
        "success": True,
        "data": recommendations,
        "count": len(recommendations),
    }), 200
