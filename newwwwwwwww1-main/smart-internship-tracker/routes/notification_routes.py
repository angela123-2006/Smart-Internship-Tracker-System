"""
==============================================================
Smart Internship Tracker System — Notification Routes
==============================================================
REST API endpoints for student notifications.
Protected by JWT authentication.
==============================================================
"""

from flask import Blueprint, request, jsonify, g
from models.notification_model import create_notification, get_student_notifications
from services.auth_middleware import login_required

notification_bp = Blueprint("notifications", __name__)

MAX_MESSAGE_LENGTH = 500


@notification_bp.route("/api/notifications", methods=["POST"])
@login_required
def api_create_notification():
    """Create a new notification for a student."""
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"success": False, "error": "Request body must be valid JSON"}), 400

    student_id = data.get("student_id")
    message = (data.get("message") or "").strip()

    errors = []
    if not student_id or not isinstance(student_id, int):
        errors.append("student_id is required and must be an integer")
    if not message or len(message) > MAX_MESSAGE_LENGTH:
        errors.append("message is required (max 500 chars)")

    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    result = create_notification(student_id, message)

    if result["success"]:
        try:
            from app import socketio
            socketio.emit("new_notification", {
                "student_id": student_id,
                "message": message,
            })
        except Exception:
            pass
        return jsonify({
            "success": True,
            "message": "Notification created successfully",
            "data": {"notification_id": result["notification_id"]},
        }), 201
    else:
        return jsonify({"success": False, "error": result["error"]}), 400


@notification_bp.route("/api/notifications/student/<int:student_id>", methods=["GET"])
@login_required
def api_get_student_notifications(student_id):
    """Retrieve all notifications for a specific student."""
    if g.current_user["student_id"] != student_id:
        return jsonify({"success": False, "error": "You can only view your own notifications"}), 403

    notifications = get_student_notifications(student_id)
    for item in notifications:
        for key, value in item.items():
            if hasattr(value, "isoformat"):
                item[key] = value.isoformat()

    return jsonify({"success": True, "data": notifications, "count": len(notifications)}), 200
