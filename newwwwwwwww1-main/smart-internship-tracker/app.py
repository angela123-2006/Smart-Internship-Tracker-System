"""
==============================================================
Smart Internship Tracker System — Main Application
==============================================================
Entry point for the Flask server with SocketIO (real-time),
CORS, rate limiting, and JWT-based authentication.
==============================================================

Usage:
    python app.py
==============================================================
"""

from flask import Flask, jsonify, send_from_directory
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import logging
from config import Config

# --- Import route blueprints ---
from routes.student_routes import student_bp
from routes.company_routes import company_bp
from routes.internship_routes import internship_bp
from routes.application_routes import application_bp
from routes.skill_routes import skill_bp
from routes.notification_routes import notification_bp
from routes.auth_routes import auth_bp

# --- SocketIO instance (created at module level for import) ---
socketio = SocketIO(cors_allowed_origins="*")

# --- Rate limiter ---
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per minute"],
    storage_uri="memory://",
)

# --- Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def create_app():
    """
    Application factory — creates and configures the Flask app.

    Returns:
        Flask: Configured application instance.
    """
    app = Flask(__name__)
    app.config["SECRET_KEY"] = Config.SECRET_KEY

    # ----------------------------------------------------------
    # Extensions
    # ----------------------------------------------------------
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    limiter.init_app(app)
    socketio.init_app(app, async_mode="threading")

    # ----------------------------------------------------------
    # Register Blueprints (each file handles its own routes)
    # ----------------------------------------------------------
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(internship_bp)
    app.register_blueprint(application_bp)
    app.register_blueprint(skill_bp)
    app.register_blueprint(notification_bp)

    # ----------------------------------------------------------
    # Rate limiting on auth endpoints
    # ----------------------------------------------------------
    limiter.limit("10 per minute")(
        app.view_functions.get("auth.login", lambda: None)
    )
    limiter.limit("5 per minute")(
        app.view_functions.get("auth.register", lambda: None)
    )

    # ----------------------------------------------------------
    # Serve the frontend dashboard UI
    # ----------------------------------------------------------
    @app.route("/", methods=["GET"])
    def index():
        """Serve the main dashboard UI."""
        static_folder = os.path.join(os.path.dirname(__file__), "static")
        return send_from_directory(static_folder, "index.html")

    # ----------------------------------------------------------
    # Serve user uploads (Resumes)
    # ----------------------------------------------------------
    @app.route("/uploads/<path:filename>", methods=["GET"])
    def serve_upload(filename):
        """Serve uploaded resumes."""
        upload_folder = os.path.join(os.path.dirname(__file__), "uploads", "resumes")
        return send_from_directory(upload_folder, filename)

    # Ensure upload directory exists
    os.makedirs(os.path.join(os.path.dirname(__file__), "uploads", "resumes"), exist_ok=True)

    # ----------------------------------------------------------
    # Health-check endpoint
    # ----------------------------------------------------------
    @app.route("/api/health", methods=["GET"])
    def health_check():
        """Verify the server is running."""
        return jsonify({
            "success": True,
            "message": "Smart Internship Tracker API is running!",
        }), 200

    # ----------------------------------------------------------
    # Custom error handlers
    # ----------------------------------------------------------
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 — route not found."""
        return jsonify({
            "success": False,
            "error": "The requested endpoint was not found",
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 — wrong HTTP method."""
        return jsonify({
            "success": False,
            "error": "HTTP method not allowed for this endpoint",
        }), 405

    @app.errorhandler(429)
    def ratelimit_error(error):
        """Handle 429 — too many requests."""
        return jsonify({
            "success": False,
            "error": "Too many requests. Please slow down.",
        }), 429

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 — unexpected server error."""
        logger.error("Internal server error: %s", error)
        return jsonify({
            "success": False,
            "error": "An internal server error occurred",
        }), 500

    return app


# ==============================================================
# Run the server
# ==============================================================
if __name__ == "__main__":
    app = create_app()
    logger.info("=" * 60)
    logger.info("  Smart Internship Tracker System")
    logger.info("  Running on http://127.0.0.1:%s", Config.PORT)
    logger.info("=" * 60)
    socketio.run(
        app,
        host="127.0.0.1",
        port=Config.PORT,
        debug=Config.DEBUG,
        allow_unsafe_werkzeug=True,
    )
