"""
==============================================================
Smart Internship Tracker System — Company Routes
==============================================================
REST API endpoints for Company operations.
==============================================================
"""

from flask import Blueprint, request, jsonify
from models.company_model import create_company, get_all_companies

company_bp = Blueprint("companies", __name__)

# ---------------------------------------------------------------
# Constants
# ---------------------------------------------------------------
MAX_NAME_LENGTH = 150
MAX_LOCATION_LENGTH = 150
MAX_INDUSTRY_LENGTH = 100
MAX_WEBSITE_LENGTH = 255


# ---------------------------------------------------------------
# POST /api/companies — Create a new company
# ---------------------------------------------------------------
@company_bp.route("/api/companies", methods=["POST"])
def api_create_company():
    """Create a new company record."""
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "error": "Request body must be valid JSON",
        }), 400

    # --- Input validation ---
    company_name = (data.get("company_name") or "").strip()
    location = (data.get("location") or "").strip()
    industry_type = (data.get("industry_type") or "").strip()
    website = (data.get("website") or "").strip() or None

    errors = []
    if not company_name or len(company_name) > MAX_NAME_LENGTH:
        errors.append("company_name is required (max 150 chars)")
    if not location or len(location) > MAX_LOCATION_LENGTH:
        errors.append("location is required (max 150 chars)")
    if not industry_type or len(industry_type) > MAX_INDUSTRY_LENGTH:
        errors.append("industry_type is required (max 100 chars)")
    if website and len(website) > MAX_WEBSITE_LENGTH:
        errors.append("website must be at most 255 chars")

    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    # --- Create the company ---
    result = create_company(company_name, location, industry_type, website)

    if result["success"]:
        return jsonify({
            "success": True,
            "message": "Company created successfully",
            "data": {"company_id": result["company_id"]},
        }), 201
    else:
        return jsonify({"success": False, "error": result["error"]}), 400


# ---------------------------------------------------------------
# GET /api/companies — List all companies
# ---------------------------------------------------------------
@company_bp.route("/api/companies", methods=["GET"])
def api_get_companies():
    """Retrieve all companies."""
    companies = get_all_companies()
    return jsonify({
        "success": True,
        "data": companies,
        "count": len(companies),
    }), 200
