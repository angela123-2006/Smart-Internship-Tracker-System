"""
==============================================================
Smart Internship Tracker System — Auth Middleware
==============================================================
Provides a decorator to protect routes that require login.
Extracts the JWT token from the Authorization header.
==============================================================
"""

from functools import wraps
from flask import request, jsonify, g
from services.auth_service import decode_token


def login_required(f):
    """
    Decorator that enforces JWT authentication on a route.

    Usage:
        @app.route("/protected")
        @login_required
        def protected():
            user = g.current_user  # dict with student_id, name, email
            ...

    Returns 401 if the token is missing, invalid, or expired.
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({
                "success": False,
                "error": "Authentication required. Please log in.",
            }), 401

        token = auth_header.split(" ", 1)[1]
        payload = decode_token(token)

        if payload is None:
            return jsonify({
                "success": False,
                "error": "Session expired or invalid. Please log in again.",
            }), 401

        # Attach user info to Flask's request-scoped g object
        g.current_user = {
            "user_id": payload.get("user_id", payload.get("student_id")), # handle old tokens gracefully if any
            "name": payload["name"],
            "email": payload["email"],
            "role": payload.get("role", "student"),
        }

        # Backwards compatibility for routes specifically requesting student_id
        if g.current_user["role"] == "student":
            g.current_user["student_id"] = g.current_user["user_id"]
        elif g.current_user["role"] == "company":
            g.current_user["company_id"] = g.current_user["user_id"]

        return f(*args, **kwargs)

    return decorated


def role_required(*roles):
    """
    Decorator that enforces specific roles for an endpoint.
    Must be stacked *after* an auth check, or it will wrap `@login_required` internally.
    """
    def decorator(f):
        @login_required
        @wraps(f)
        def decorated(*args, **kwargs):
            if g.current_user.get("role") not in roles:
                return jsonify({
                    "success": False,
                    "error": f"Access denied. Requires one of roles: {', '.join(roles)}",
                }), 403
            return f(*args, **kwargs)
        return decorated
    return decorator
