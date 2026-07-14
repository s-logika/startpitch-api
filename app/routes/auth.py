from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services.auth_service import (
    USERS,
    authenticate_user,
    issue_tokens,
    register_user,
)

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth_bp.post("/register")
def register():
    data = request.get_json() or {}
    user = register_user(data.get("email", ""), data.get("password", ""), data.get("role", "founder"))
    return jsonify(user), 201


@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    user = authenticate_user(data.get("email", ""), data.get("password", ""))
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    tokens = issue_tokens(user)
    return jsonify(tokens), 200


@auth_bp.post("/oauth/google")
def oauth_google():
    return jsonify({"provider": "google", "status": "stub"}), 200


@auth_bp.post("/oauth/linkedin")
def oauth_linkedin():
    return jsonify({"provider": "linkedin", "status": "stub"}), 200


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    user = next((u for u in USERS.values() if str(u["id"]) == str(user_id)), None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(issue_tokens(user)), 200
