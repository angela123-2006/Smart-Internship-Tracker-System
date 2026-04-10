"""
==============================================================
Smart Internship Tracker System — Application Routes
==============================================================
REST API endpoints for internship applications, status updates,
and placement cell dashboard statistics.
Emits real-time SocketIO events on application changes.
==============================================================
"""

from flask import Blueprint, request, jsonify, g
from models.application_model import (
    create_application,
    get_student_applications,
    update_application_status,
    get_all_applications,
    get_application_statistics,
)
from services.auth_middleware import login_required

application_bp = Blueprint("applications", __name__)


def _emit_realtime(event, data):
    """
    Emit a SocketIO event for real-time updates.
    Imported lazily to avoid circular imports.
    """
    try:
        from app import socketio
        socketio.emit(event, data)
    except Exception:
        pass  # Non-critical; log silently if SocketIO unavailable


# ---------------------------------------------------------------
# POST /api/applications — Apply for an internship
# ---------------------------------------------------------------
@application_bp.route("/api/applications", methods=["POST"])
@login_required
def api_create_application():
    """Record a student's application for an internship."""
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "error": "Request body must be valid JSON",
        }), 400

    # Use the logged-in user's student_id
    student_id = g.current_user["student_id"]
    internship_id = data.get("internship_id")
    application_date = (data.get("application_date") or "").strip()

    errors = []
    if not internship_id or not isinstance(internship_id, int):
        errors.append("internship_id is required and must be an integer")
    if not application_date:
        errors.append("application_date is required (YYYY-MM-DD)")

    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    # --- Create the application ---
    result = create_application(student_id, internship_id, application_date)

    if result["success"]:
        # Emit real-time event
        _emit_realtime("application_created", {
            "application_id": result["application_id"],
            "student_name": g.current_user["name"],
            "internship_id": internship_id,
        })

        return jsonify({
            "success": True,
            "message": "Application submitted successfully",
            "data": {"application_id": result["application_id"]},
        }), 201
    else:
        return jsonify({"success": False, "error": result["error"]}), 400


# ---------------------------------------------------------------
# GET /api/applications/student/<id> — Student's applications
# ---------------------------------------------------------------
@application_bp.route("/api/applications/student/<int:student_id>",
                      methods=["GET"])
@login_required
def api_get_student_applications(student_id):
    """Retrieve all applications for a specific student."""
    # Students can only view their own applications
    if g.current_user["student_id"] != student_id:
        return jsonify({
            "success": False,
            "error": "You can only view your own applications",
        }), 403

    applications = get_student_applications(student_id)

    for item in applications:
        for key, value in item.items():
            if hasattr(value, "isoformat"):
                item[key] = value.isoformat()

    return jsonify({
        "success": True,
        "data": applications,
        "count": len(applications),
    }), 200


# ---------------------------------------------------------------
# PUT /api/applications/<id>/status — Update application status
# ---------------------------------------------------------------
@application_bp.route("/api/applications/<int:application_id>/status",
                      methods=["PUT"])
@login_required
def api_update_status(application_id):
    """Update the status of an application (used by companies/admin)."""
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "error": "Request body must be valid JSON",
        }), 400

    new_status = (data.get("status") or "").strip()
    if not new_status:
        return jsonify({
            "success": False,
            "error": "status is required",
        }), 400

    result = update_application_status(application_id, new_status)

    if result["success"]:
        # Emit real-time event for status change
        _emit_realtime("status_updated", {
            "application_id": application_id,
            "new_status": new_status,
        })

        return jsonify({
            "success": True,
            "message": result["message"],
        }), 200
    else:
        status_code = 404 if "not found" in result["error"].lower() else 400
        return jsonify({
            "success": False,
            "error": result["error"],
        }), status_code


# ---------------------------------------------------------------
# GET /api/applications — All applications
# ---------------------------------------------------------------
@application_bp.route("/api/applications", methods=["GET"])
@login_required
def api_get_all_applications():
    """Retrieve all applications (for feed/dashboard)."""
    applications = get_all_applications()

    for item in applications:
        for key, value in item.items():
            if hasattr(value, "isoformat"):
                item[key] = value.isoformat()

    return jsonify({
        "success": True,
        "data": applications,
        "count": len(applications),
    }), 200


# ---------------------------------------------------------------
# GET /api/applications/statistics — Status breakdown
# ---------------------------------------------------------------
@application_bp.route("/api/applications/statistics", methods=["GET"])
@login_required
def api_get_statistics():
    """Get application counts grouped by status."""
    stats = get_application_statistics()
    return jsonify({
        "success": True,
        "data": stats,
    }), 200
