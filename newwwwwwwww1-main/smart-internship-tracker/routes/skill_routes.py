"""
==============================================================
Smart Internship Tracker System — Skill Routes
==============================================================
REST API endpoints for student skill management.
Protected by JWT authentication.
==============================================================
"""

from flask import Blueprint, request, jsonify, g
from models.skill_model import add_skill, get_student_skills
from services.auth_middleware import login_required

skill_bp = Blueprint("skills", __name__)

MAX_SKILL_NAME_LENGTH = 100


@skill_bp.route("/api/skills", methods=["POST"])
@login_required
def api_add_skill():
    """Add a skill entry for the logged-in student."""
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"success": False, "error": "Request body must be valid JSON"}), 400

    student_id = g.current_user["student_id"]
    skill_name = (data.get("skill_name") or "").strip()
    proficiency_level = (data.get("proficiency_level") or "").strip()

    errors = []
    if not skill_name or len(skill_name) > MAX_SKILL_NAME_LENGTH:
        errors.append("skill_name is required (max 100 chars)")
    if not proficiency_level:
        errors.append("proficiency_level is required (Beginner, Intermediate, or Advanced)")

    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    result = add_skill(student_id, skill_name, proficiency_level)

    if result["success"]:
        try:
            from app import socketio
            socketio.emit("skill_added", {
                "student_name": g.current_user["name"],
                "skill_name": skill_name,
            })
        except Exception:
            pass
        return jsonify({
            "success": True,
            "message": "Skill added successfully",
            "data": {"skill_id": result["skill_id"]},
        }), 201
    else:
        return jsonify({"success": False, "error": result["error"]}), 400


@skill_bp.route("/api/skills/student/<int:student_id>", methods=["GET"])
@login_required
def api_get_student_skills(student_id):
    """Retrieve all skills for a specific student."""
    skills = get_student_skills(student_id)
    return jsonify({"success": True, "data": skills, "count": len(skills)}), 200
